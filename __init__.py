from flask import Flask, render_template, request
from app.database import Database

app = Flask(__name__)


@app.route("/")
def initialize_database_connection():
    return render_template("website.html")


@app.route('/submit', methods=["GET", "POST"])
def submit():
    # initiate Database Connection
    connection = Database()
    try:
        if request.method == "POST":
            # handle user entries
            author = request.form["author"]
            title = request.form["title"]
            file = request.files["file"].read()
            #

            # write entries in database for further processing
            connection.query_insert_into_database(author, title, file)
        else:
            print('Error: Connection not established'.format())

    except Exception as e:
        logfile = open('exceptions.log', 'w')
        logfile.write("Failed to connect {0}: {1}\n".format(str(connection), str(e)))

    return render_template("submit.html")


@app.route('/submit/output')
def output():
    connection = Database()
    try:
        user_output = connection.query_to_mirror_database()
        return render_template('output.html', output=user_output)
    except Exception as e:
        logfile = open('exceptions.log', 'w')
        logfile.write("Failed to connect {0}: {1}\n".format(str(connection), str(e)))


@app.route('/submit/output/result', methods=['GET', 'POST'])
def export_to_process():
    if request.method == 'POST':
        checkbox = request.form.getlist('checkbox')
        # nativ --> get all values from the checked checkboxes with the name checkbox
        connection = Database()
        # matches are the words from the user text matches with the names in the geographic database
        matches = {}
        # paragraph --> user selection --> one text is one paragraph
        paragraphs = {}
        # checkbox is the user selection on the mirror database view
        for entry_id in checkbox:
            entry = connection.get_user_selection(entry_id)
            words = connection.divide_user_selection(entry)
            # paragraph key is the entry_id -> value = all words from the user text
            paragraphs[entry_id] = words
        for key in paragraphs:
            words = paragraphs[key]
            for word in words:
                if word not in matches:
                    local_entity = connection.query_to_export_local_entity()
                    records = connection.get_records(local_entity)
                    full_names = connection.get_names(records, None, [])
                    found_matches = connection.lookup([word], full_names)
                    if found_matches is not None and len(found_matches) > 0:
                        # check if there are matches -> word is key and found_match is value
                        matches[word] = found_matches
    # print(matches)
    return render_template("result.html", paragraphs=paragraphs, matches=matches)


if __name__ == "__main__":
    app.run(debug=False)
