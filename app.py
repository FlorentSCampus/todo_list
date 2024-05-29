from bottle import route, run, debug, template, request, static_file, error
import sqlite3

def create_db():
    conn = sqlite3.connect("todo_list/todo.db")
    conn.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL)")
    conn.execute("INSERT INTO todo (task, status) VALUES ('Read A-byte-of-python to get a good introduction into Python', 0)")
    conn.execute("INSERT INTO todo (task, status) VALUES ('Visit the Python website', 1)")
    conn.execute("INSERT INTO todo (task, status) VALUES ('Test various editors for and check the syntax highlighting', 1)")
    conn.execute("INSERT INTO todo (task, status) VALUES ('Choose your favorite WSGI-Framework', 0)")
    conn.commit()

@route("/todo")
def todo_list():
    conn = sqlite3.connect("todo_list/todo.db")
    c = conn.cursor()
    # c.execute("SELECT id, task FROM todo WHERE status = 1")
    c.execute("SELECT id, task FROM todo")
    res = c.fetchall()
    c.close()
    output = template("todo_list/make_table", rows = res)
    return output

@route("/new", method = "GET")
def new_item():
    if request.GET.save:
        new = request.GET.task.strip()
        conn = sqlite3.connect("todo_list/todo.db")
        c = conn.cursor()
        c.execute("INSERT INTO todo (task, status) VALUES (?, ?)", (new, 1))
        new_id = c.lastrowid
        conn.commit()
        c.close()
        return "<p>The new task was inserted into the database, the ID is %s</p>" % new_id
    else:
        return template("todo_list/new_task")

@route("/edit/<no:int>", method = "GET")
def edit_item(no):
    if request.GET.save:
        edit = request.GET.task.strip()
        status = request.GET.status.strip()

        if status == "open":
            status = 1
        else:
            status = 0

        conn = sqlite3.connect("todo_list/todo.db")
        c = conn.cursor()
        c.execute("UPDATE todo SET task = ?, status = ? WHERE id = ?", (edit, status, no))
        conn.commit()

        return "<p>The item number %s was successfully updated</p>" % no
    else:
        conn = sqlite3.connect("todo_list/todo.db")
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id = ?", (str(no),))
        cur_data = c.fetchone()

        return template("todo_list/edit_task", old = cur_data, no = no)
    
@route("/item<item:re:[0-9]+>")
def show_item(item):
    conn = sqlite3.connect("todo_list/todo.db")
    c = conn.cursor()
    c.execute("SELECT task FROM todo WHERE id = ?", (item,))
    result = c.fetchall()
    c.close()
    if not result:
        return "This item number does not exist!"
    else:
        return "Task: %s" % result[0]

@route("/help")
def help():
    return static_file("help.html", root = "todo_list")

@route("/json<json:re:[0-9]+>")
def show_json(json):
    conn = sqlite3.connect("todo_list/todo.db")
    c = conn.cursor()
    c.execute("SELECT task FROM todo WHERE id = ?", (json,))
    result = c.fetchall()
    c.close()

    if not result:
        return {"task": "This item number does not exist!"}
    else:
        return {"task": result[0]}
    
@error(403)
def mistake403(code):
    return 'The parameter you passed has the wrong format!'

@error(404)
def mistake404(code):
    return 'Sorry, this page does not exist!'

run(reloader = True)