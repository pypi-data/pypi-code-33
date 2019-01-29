#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, urlparse, pprint, traceback
from pweb import http
from pweb.template import Template
from pweb.utils.datastructs import storage

whereami = os.path.join(os.getcwd(), __file__)
whereami = os.path.sep.join(whereami.split(os.path.sep)[:-1])

debugerror_t = """\
<%
if undefined("exception_type"): exception_type=""
if undefined("exception_value"): exception_value=""
if undefined("frames"): frames = []

exception_type = escape(exception_type)
exception_value = escape(exception_value)
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <meta name="robots" content="NONE,NOARCHIVE" />
  <title><%=safeutf8(exception_type)%>&nbsp;at&nbsp;<%=safeutf8(request.path)%></title>
  <style type="text/css">
    html * { padding:0; margin:0; }
    body * { padding:10px 20px; }
    body * * { padding:0; }
    body { font:small sans-serif; }
    body>div { border-bottom:1px solid #ddd; }
    h1 { font-weight:normal; }
    h2 { margin-bottom:.8em; }
    h2 span { font-size:80%; color:#666; font-weight:normal; }
    h3 { margin:1em 0 .5em 0; }
    h4 { margin:0 0 .5em 0; font-weight: normal; }
    code { font-weight: bold; }
    table { border:1px solid #ccc; border-collapse: collapse; background:white; }
    tbody td, tbody th { vertical-align:top; padding:2px 3px; }
    thead th { padding:1px 6px 1px 3px; background:#fefefe; text-align:left; font-weight:normal; font-size:11px; border:1px solid #ddd; }
    tbody th { text-align:right; color:#666; padding-right:.5em; }
    table.vars { margin:5px 0 2px 40px; }
    table.vars td, table.req td { font-family:monospace; }
    table td.code { width:100%;}
    table td.code div { overflow:hidden; }
    table.source th { color:#666; }
    table.source td { font-family:monospace; white-space:pre; border-bottom:1px solid #eee; }
    ul.traceback { list-style-type:none; }
    ul.traceback li.frame { margin-bottom:1em; }
    div.context { margin: 10px 0; }
    div.context ol { padding-left:30px; margin:0 10px; list-style-position: inside; }
    div.context ol li { font-family:monospace; white-space:pre; color:#666; cursor:pointer; }
    div.context ol.context-line li { color:black; background-color:#ccc; }
    div.context ol.context-line li span { float: right; }
    div.commands { margin-left: 40px; }
    div.commands a { color:black; text-decoration:none; }
    #skyblue { background: #ccdeff; }
    #skyblue h2 { font-weight: normal; color: #666; }
    #explanation { background:#eee; }
    #template, #template-not-exist { background:#f6f6f6; }
    #template-not-exist ul { margin: 0 0 0 20px; }
    #traceback { background:#eee; }
    #requestinfo { background:#f6f6f6; padding-left:120px; }
    #skyblue table { border:none; background:transparent; }
    #requestinfo h2, #requestinfo h3 { position:relative; margin-left:-100px; }
    #requestinfo h3 { margin-bottom:-1em; }
    .error { background: #ffc; }
    .specific { color:#cc3300; font-weight:bold; }
  </style>
  <script type="text/javascript">
  <!--
    function getElementsByClassName(oElm, strTagName, strClassName){
        // Written by Jonathan Snook, http://www.snook.ca/jon; 
        // Add-ons by Robert Nyman, http://www.robertnyman.com
        var arrElements = (strTagName == "*" && document.all)? document.all :
        oElm.getElementsByTagName(strTagName);
        var arrReturnElements = new Array();
        strClassName = strClassName.replace(/\-/g, "\\-");
        var oRegExp = new RegExp("(^|\\s)" + strClassName + "(\\s|$$)");
        var oElement;
        for(var i=0; i<arrElements.length; i++){
            oElement = arrElements[i];
            if(oRegExp.test(oElement.className)){
                arrReturnElements.push(oElement);
            }
        }
        return (arrReturnElements)
    }
    function hideAll(elems) {
      for (var e = 0; e < elems.length; e++) {
        elems[e].style.display = 'none';
      }
    }
    window.onload = function() {
      hideAll(getElementsByClassName(document, 'table', 'vars'));
      hideAll(getElementsByClassName(document, 'ol', 'pre-context'));
      hideAll(getElementsByClassName(document, 'ol', 'post-context'));
    }
    function toggle() {
      for (var i = 0; i < arguments.length; i++) {
        var e = document.getElementById(arguments[i]);
        if (e) {
          e.style.display = e.style.display == 'none' ? 'block' : 'none';
        }
      }
      return false;
    }
    function varToggle(link, id) {
      toggle('v' + id);
      var s = link.getElementsByTagName('span')[0];
      var uarr = String.fromCharCode(0x25b6);
      var darr = String.fromCharCode(0x25bc);
      s.innerHTML = s.innerHTML == uarr ? darr : uarr;
      return false;
    }
    //-->
  </script>
</head>
<body>

<%
def dicttable(d, kls='req', id=None):
    items = d and d.items() or []
    items.sort()
    return dicttable_items(items, kls, id)
        
def dicttable_items(items, kls='req', id=None):
    if items:
        result = '<table class="%s"' % kls
        if id: result += ' id="%s"' % id
        result += '><thead><tr><th>Variable</th><th>Value</th></tr></thead>'
        result += '<tbody>'
        for k, v in items:
            result += '<tr><td>%s</td><td class="code"><div>%s</div></td></tr>'% (k, prettify(v))
        result += '</tbody>'
        result += '</table>'
    else:
        result = "<p>No data.</p>"
    return result
%>
<div id="skyblue">
  <h1><%=safeutf8(exception_type)%>&nbsp;at&nbsp;<%=safeutf8(request.path)%></h1>
  <h2><%=safeutf8(exception_value)%></h2>
  <table><tr>
    <th>Python</th>
    <td><%#if frames%><%=safeutf8(frames[0].filename)%>&nbsp;in&nbsp;<%=safeutf8(frames[0].function)%>, line <%=safeutf8(frames[0].lineno)%><%#endif%></td>
  </tr><tr>
    <th>Web</th>
    <td><%=safeutf8(request.method)%> <%=safeutf8(request.home)%><%=safeutf8(request.path)%></td>
  </tr></table>
</div>
<div id="traceback">
  <h2>Traceback <span>(innermost first)</span></h2>
  <ul class="traceback">
<%
for frame in frames:
    print '''<li class="frame">'''
    print '''<code>%s</code> in <code>%s</code>'''% (frame.filename, frame.function)
    if frame.context_line is not None:
        print '''<div class="context" id="c%s">'''% frame.id
        if frame.pre_context:
            print '''<ol start="%s" class="pre-context" id="pre%s">'''% (frame.pre_context_lineno, frame.id)
            for line in frame.pre_context:
                print '''<li onclick="toggle('pre%s', 'post%s')">%s</li>'''% (frame.id, frame.id, line)
            print '''</ol>'''
            print '''<ol start="%s" class="context-line">'''% frame.lineno
            print '''<li onclick="toggle('pre%s', 'post%s')">%s<span>...</span></li>'''% (frame.id, frame.id, frame.context_line)
            print '''</ol>'''

        if frame.post_context:
            print '''<ol start='%s' class="post-context" id="post%s">'''% (frame.lineno + 1, frame.id)
            for line in frame.post_context:
                print '''<li onclick="toggle('pre%s', 'post%s')">%s</li>'''% (frame.id, frame.id, line)
            print '''</ol>'''
        print '''</div>'''
    
    if frame.vars:
        print '''<div class="commands">'''
        print '''<a href='#' onclick="return varToggle(this, '%s')"><span>&#x25b6;</span> Local vars</a>'''% frame.id
        # $inspect.formatargvalues(*inspect.getargvalues(frame['tb'].tb_frame))
        print '''</div>'''
        print dicttable(frame.vars, kls='vars', id=('v' + str(frame.id)))
    print '''</li>'''
%>
  </ul>
</div>

<div id="requestinfo">
<%
if request.output or request.headers:
    print '<h2>Response so far</h2>'
    print '<h3>HEADERS</h3>'
    print dicttable_items(request.headers)

    print '<h3>BODY</h3>'
    print '<p class="req" style="padding-bottom: 2em"><code>'
    print request.output
    print '</code></p>'
%>
<h2>Request information</h2>

<h3>INPUT</h3>
<%= dicttable(request.input(_unicode=False))%>

<h3 id="cookie-info">COOKIES</h3>
<%= dicttable(request.cookies())%>

<h3 id="meta-info">META</h3>
<%
newctx = [(k, v) for (k, v) in request.iteritems() if not k.startswith('_') and not isinstance(v, dict)]
%>
<%=dicttable(dict(newctx))%>

<h3 id="meta-info">ENVIRONMENT</h3>
<%=dicttable(request.env)%>
</div>

<div id="explanation">
  <p>
    You're seeing this error because you have <code>settings.DEBUG</code>
    set to <code>True</code>. Set that to <code>False</code> if you don't want to see this.
  </p>
</div>

</body>
</html>
"""

debugerror_r = None


def debugerror():
    def _get_lines_from_file(filename, lineno, context_lines):
        try:
            source = open(filename).readlines()
            lower_bound = max(0, lineno - context_lines)
            upper_bound = lineno + context_lines

            pre_context = \
                [line.strip('\n') for line in source[lower_bound:lineno]]
            context_line = source[lineno].strip('\n')
            post_context = \
                [line.strip('\n') for line in source[lineno + 1:upper_bound]]

            return lower_bound, pre_context, context_line, post_context
        except (OSError, IOError, IndexError):
            return None, [], None, []

    exception_type, exception_value, tback = sys.exc_info()
    frames = []
    while tback is not None:
        filename = tback.tb_frame.f_code.co_filename
        function = tback.tb_frame.f_code.co_name
        lineno = tback.tb_lineno - 1

        # hack to get correct line number for templates
        lineno += tback.tb_frame.f_locals.get("__lineoffset__", 0)

        pre_context_lineno, pre_context, context_line, post_context = _get_lines_from_file(filename, lineno, 7)

        frames.append(storage({
            'tback': tback,
            'filename': filename,
            'function': function,
            'lineno': lineno,
            'vars': tback.tb_frame.f_locals,
            'id': id(tback),
            'pre_context': pre_context,
            'context_line': context_line,
            'post_context': post_context,
            'pre_context_lineno': pre_context_lineno,
        }))
        tback = tback.tb_next
    frames.reverse()
    urljoin = urlparse.urljoin

    def prettify(x):
        try:
            out = pprint.pformat(x)
        except Exception, e:
            out = '[could not display: <' + e.__class__.__name__ + ': ' + str(e) + '>]'
        return out

    global debugerror_r
    if debugerror_r is None:
        debugerror_r = Template(debugerror_t, filename=__file__)

    t = debugerror_r
    globals = {'request': http.request, 'dict': dict, 'str': str, 'prettify': prettify}
    t.env.update(globals)
    return t(exception_type=exception_type, exception_value=exception_value, frames=frames)


def debugerrorRsp():
    return http._InternalError(debugerror())
