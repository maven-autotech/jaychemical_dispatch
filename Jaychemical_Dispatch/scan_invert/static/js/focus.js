function input1(event)
{
    var bar1=document.getElementById('serial').value;
    if(!bar1)
    {
        $("#serial").focus();
    }
}

function input2(event)
{
    var bar1=document.getElementById('location').value;
    if(!bar1)
    {
        $("#location").focus();
    }
}


function myFunction1(event)
{
        console.log("BEFORE >>>>>>>>")
        var x = document.getElementById("myaudio").play();
        console.log("after >>>>>>>>>>>>>>");
}


function myFunction2(event)
{
        console.log("BEFORE >>>>>>>>")
        var x = document.getElementById("myaudio1").play();
        console.log("after >>>>>>>>>>>>>>");
}