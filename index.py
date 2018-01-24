# coding: utf-8

import MySQLdb
import sys
import datetime
import cgi


def printer(list, color, legend, output):
    for minion in list:
        minionName = str(minion[0])
        minionTimestamp = str(minion[1]) 
        minionStatus = str(minion[2])
        minionComment = str(minion[3])
        if minionStatus == 'None':
            minionStatus = "<form action=\"\" method=\"post\"><input type=\"hidden\" name=\"minion\" value=\"" + minionName + "\"/><input type=\"hidden\" name=\"status\" value=\"1\" />\n \
                <input type=\"submit\" id=\"unpressedbutton\" value=\"в пути\" /></form>\n \
                <form action=\"\" method=\"post\"><input type=\"hidden\" name=\"minion\" value=\"" + minionName + "\"/><input type=\"hidden\" name=\"status\" value=\"2\" />\n \
                <input type=\"submit\" id=\"unpressedbutton\" value=\"замена\" /></form>\n"
        if minionStatus == '1':
            minionStatus = "<form action=\"\" method=\"post\"><input type=\"hidden\" name=\"minion\" value=\"" + minionName + "\"/><input type=\"hidden\" name=\"status\" value=\"0\" />\n \
                <input type=\"submit\" id=\"pressedbutton\" value=\"в пути\" /></form>\n \
                <form action=\"\" method=\"post\"><input type=\"hidden\" name=\"minion\" value=\"" + minionName + "\"/><input type=\"hidden\" name=\"status\" value=\"2\" />\n \
                <input type=\"submit\" id=\"unpressedbutton\"  value=\"замена\" /></form>\n"
        if minionStatus == '2':
            minionStatus = "<form action=\"\" method=\"post\"><input type=\"hidden\" name=\"minion\" value=\"" + minionName + "\"/><input type=\"hidden\" name=\"status\" value=\"1\" />\n \
                <input type=\"submit\" id=\"unpressedbutton\" value=\"в пути\" /></form>\n \
                <form action=\"\" method=\"post\"><input type=\"hidden\" name=\"minion\" value=\"" + minionName + "\"/><input type=\"hidden\" name=\"status\" value=\"0\" />\n \
                <input type=\"submit\" id=\"pressedbutton\" value=\"замена\" /></form>\n"
        if minionComment == 'None':
            minionStatus += "<button onclick=\"document.getElementById('tr" + minionName + "').style.display = 'block';\" id=\"unpressedbutton\">коммент↵</button>\n \
                </td></tr><tr id=\"tr" + minionName + "\" style=\"display:none;\"><td colspan=\"3\" id=\"comment\">\n \
                <form action=\"\" method=\"post\"><input type=\"hidden\" name=\"minion\" value=\"" + minionName + "\"/>\n \
                <input type=\"text\" name=\"comment\" value=\"\" size=\"60\"/>\n \
                <input type=\"submit\"/ value=\"OK\"></form></td></tr>"
        else:
            minionStatus += "<button onclick=\"document.getElementById('tr" + minionName + "').style.display = 'block';\" id=\"pressedbutton\">коммент↵</button>\n \
                </td></tr><tr id=\"tr" + minionName + "\" style=\"display:none;\"><td colspan=\"3\" id=\"comment\">\n \
                <form action=\"\" method=\"post\"><input type=\"hidden\" name=\"minion\" value=\"" + minionName + "\"/>\n \
                <input type=\"text\" name=\"comment\" id=\"txt" + minionName + "\"value=\""+ minionComment + "\" size=\"60\"/>\n \
                <input type=\"button\" onclick=\"document.getElementById('txt" + minionName + "').value = ''\" value=\"X\">\n \
                <input type=\"submit\"/ value=\"OK\"></form></td></tr>\n"
        output += "<tr><td><p id=\""+color+"\">" + minionName + "</p></td><td><p id=\""+color+"\">" + minionTimestamp + "</p></td><td>" + minionStatus + "</td>"
    return(output)

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])

    try:
        db = MySQLdb.connect(host="localhost", user="salter", passwd="maBLDw9hMddCCUVjb1mN", db="salter", charset='utf8')
    except:
        sys.exit("Cannot connect to mysql")
    dbc = db.cursor()

    #POST data processing
    output = ''
    request_body = env['wsgi.input']
    fs = cgi.FieldStorage(fp=request_body, environ=env, keep_blank_values=1)
    postStatus = str(fs.getvalue('status'))
    postMinion = str(fs.getvalue('minion'))
    postComment = str(fs.getvalue('comment'))
    postComment = cgi.escape(postComment)
    
    #write POST data to mysql

    if postComment != 'None':
        request = "UPDATE minions SET comment = '" + postComment + "' WHERE minion_name = '" + postMinion + "'"
        if postComment == '':
            request = "UPDATE minions SET comment = NULL WHERE minion_name = '" + postMinion + "'"
        dbc.execute(request)
        db.commit()
        
    if postStatus != 'None':
        if postStatus == '1':
            request = "UPDATE minions SET status = '1' WHERE minion_name = '" + postMinion + "'"
        elif postStatus == '2':
            request = "UPDATE minions SET status = '2' WHERE minion_name = '" + postMinion + "'"
        elif postStatus == '0':
            request = "UPDATE minions SET status = NULL WHERE minion_name = '" + postMinion + "'"
        dbc.execute(request)
        db.commit()

    request = "SELECT * FROM minions WHERE seen_timestamp <= (NOW() - INTERVAL 6 DAY) OR seen_timestamp IS NULL ORDER BY minion_name"
    dbc.execute(request)
    resultRed = dbc.fetchall()
    lostCount = len(resultRed)

    request = "SELECT * FROM minions WHERE seen_timestamp > (NOW() - INTERVAL 6 DAY) AND seen_timestamp < (NOW() - INTERVAL 1 DAY) ORDER BY minion_name"
    dbc.execute(request)
    resultYellow = dbc.fetchall()

    request = "SELECT * FROM minions WHERE seen_timestamp >= (NOW() - INTERVAL 1 DAY) ORDER BY minion_name"
    dbc.execute(request)
    resultGreen = dbc.fetchall()

    totalCount = len(resultRed) + len (resultYellow) + len(resultGreen)

    legend = "<tr><td width=\"100\"></td><td width=\"500\"><p id=\"green\">Отзывался не больше 24 часов назад</p></td></tr>\n \
        <tr><td width=\"100\"></td><td width=\"500\"><p id=\"yellow\">Отзывался 1-6 дней назад</p></td></tr>\n \
        <tr><td width=\"100\"></td><td width=\"500\"><p id=\"red\">Отзывался больше 6 дней назад (" + str(lostCount) + ")</p></td></tr>\n \
        <tr><td width=\"100\"></td><td width=\"500\"><p id=\"grey\">Всего " + str(totalCount) + "</p></td></tr>\n"

    #not used!
    javaFunc = "<script>function toggle(el) {\n \
        if (el.style.display === \"none\") {\n \
            el.style.display = \"block\";\n \
        } else {\n \
            el.style.display = \"none\";\n \
        }}</script>\n"
    
    output += "<html><head><meta charset=\"utf-8\"><title>Salter</title>\n \
        <style>#red { background-color: lightsalmon; font-family: arial; font-weight: bold; }</style>\n \
        <style>#green{ background-color: darkseagreen; font-family: arial; font-weight: bold; }</style>\n \
        <style>#yellow{ background-color: palegoldenrod; font-family: arial; font-weight: bold; }</style>\n \
        <style>#grey{ background-color: lightgrey; font-family: arial; font-weight: bold; }</style>\n \
        <style>#unpressedbutton { font-size: 10px; }</style>\n \
        <style>#pressedbutton{ font-size: 10px; background-color: limegreen; }</style>\n \
        <style>a:link {color: black; } a:visited { color: black; } a:hover { color: red; }\n \
        <style>a.on:link, a.on:hover, a.on:visited, a.on:active { font-size: 10px; font-family: arial; background-color: limegreen; }</style>\n \
        <style>a.off:link, a.off:hover, a.off:visited, a.off:active { font-size: 10px; font-family: arial; }</style>\n \
        <style>form { display: inline; margin: 0px; padding: 0px; }</style>\n \
        <style>#comment{ font-family:arial; font-size: 10px; margin: 0px; padding: 0px; }</style>\n \
        </head><body><div style=\"float: left; width: 65%; padding: 10px;\"><table>\n \
        <tr><td width=\"500\"><p id=\"grey\">УЗЕЛ</p></td><td><p id=\"grey\">ПОСЛЕДНИЙ ОТВЕТ</p></td><td><p id=\"grey\">СТАТУС</p></td></tr>\n"

    output = printer(resultRed, "red", legend, output)
    output = printer(resultYellow, "yellow", legend, output)
    output = printer(resultGreen, "green", legend, output)
    
    output += "</table></div><div style=\"float: right; padding: 10px;\">\n \
        <table>" + legend + "</table></div></body></html>"

    byteOutput = str.encode(output)
    return(byteOutput)

#print(application(1,2))
