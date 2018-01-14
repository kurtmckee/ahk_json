; runner.ahk uses STDIN and STDOUT to accept unit test inputs.
; Python submits unit test data through STDIN and runner.ahk
; loads and dumps the JSON data back through STDOUT to confirm
; that the data is identical.

#include <json>


stdin := fileopen("*", "r", "UTF-8")
stdout := fileopen("*", "w", "UTF-8")


read()
{
    global stdin

    ; Loop until a newline is encountered.
    blob := ""
    loop,
    {
        byte := stdin.read(1)
        blob .= byte
        if (byte == chr(10))
        {
            break
        }
    }
    blob := strreplace(blob, "`n")

    info := json_load(blob)

    return info
}


write(info)
{
    global stdout

    blob := json_dump(info)

    stdout.write(blob)
    stdout.write(chr(10))
    stdout.read(0)
}


identity(parameters)
{
    return parameters
}


load_file(parameters)
{
    fileread, blob, % parameters["filename"]
    return json_load(blob)
}


exit_ahk(parameters)
{
    exitapp, 2
}


loop
{
    parameters := read()
    function := func(parameters["function"])
    data := function.call(parameters)
    write(data)
}
