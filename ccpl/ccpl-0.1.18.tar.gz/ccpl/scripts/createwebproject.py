from ccpl.console import printc

import sys
import os

player = False

if 'player' in sys.argv:
    player = True

try:
    os.mkdir("iSource")
    os.mkdir("CCWL")
except FileExistsError:
    pass

with open("CCWL/CCJSL.js", "w+") as ccjsl:
    ccjsl.write("""function gebi(id) {
    return document.getElementById(id)
}
function gebc(class) {
    return document.getElementsByClassName(class)[0]
}
function gebcs(class) {
    return document.getElementsByClassName(class)
}""")

with open("CCWL/CCCSSL.css", "w+") as cccssl:
    cccssl.write("""body {
	width: 100vw;
	min-height: 100vh;
	margin: 0;
	position: absolute;
	top: 0;
	left: 0;
}
.unselectable {
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}""")

with open("index.html", 'w+') as index:
    index.write("""<html>
<head>
    <title>New project</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="index.css">
    <link rel="stylesheet" href="CCWL/CCCSSL.css">
</head>
<body>
    <div class="container">
        <div class="welcome unselectable">Welcome!<br>You've just created a blank web project!</div>
    </div>
    <div class="backdrop1"></div>
    <div class="backdrop2"></div>
<script src="CCWL/CCJSL.js"></scripts>

<!--Yer scripts go 'ere-->

</body>
</html>""")

with open("index.css", "w+") as index:
    index.write("""body {
    font-family: "Segoe UI", sans-serif;
    display: flex;
}
.backdrop1 {
    width: 50vw;
    height: 100vh;
    background-color: #202020;
}
.backdrop2 {
    width: 50vw;
    height: 100vh;
    background-color: #606060;
}
.container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: grid;
    grid: 1fr/1fr 18fr 1fr;
    filter: drop-shadow(0em 0em 0.1em black);
}
.welcome {
    grid-area: 1/2;
    display: grid;
    place-items: center;
    font-size: 2em;
    text-align: center;
    background-color: white;
    clip-path: polygon(10% 0%, 100% 0%, 90% 100%, 0% 100%);
}""")