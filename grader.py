
from glob import glob
import nbformat


def _extract_answer_from_cell(cell):
    #
    def get_expected_answer():
        expected_answer = []
        found = False
        for line in cell.source.splitlines():
            if found is True:
                line = line.strip()
                if len(line) == 0 or line[0] != "#":
                    found = False
                if len(line.strip()) > 0 and line[0] == "#":
                    line = line[2:] if len(line) > 0 and line[0:2] == "# " else line
                    line = line[1:] if len(line) > 0 and line[0] == "#" else line
                    line = line.replace("\xa0", "")
                    line = line[:-1] if len(line) > 0 and line[-1] == "\n" else line
                    expected_answer.append(line)
            if "# Rta/" in line:
                found = True

        expected_answer = [line.replace("# ", "") for line in expected_answer]
        if len(expected_answer):
            return "\n".join(expected_answer)
        return None

    def get_computed_answer():
        output_text = None
        text = cell.outputs
        if len(text) > 0:
            text = text[0]
            if text["output_type"] == "execute_result":
                if isinstance(text["data"], dict):
                    output_text = text["data"]["text/plain"]
            if text["output_type"] == "stream":
                output_text = text["text"]
        return output_text

    return get_expected_answer(), get_computed_answer()


def _extract_answers_from_notebook(file):
    notebook = nbformat.read(file, as_version=4)
    answers = {}
    for i_cell, cell in enumerate(notebook.cells):
        if cell.cell_type == "code" and "# Rta/" in cell.source:
            expected_answer, computed_answer = _extract_answer_from_cell(cell)
            if expected_answer is not None:
                answers[i_cell] = expected_answer, computed_answer
    return answers


def _format_text(text):
    if text is None:
        return None
    lines = text.splitlines()
    lines = [line.split() for line in lines]
    lines = [" ".join(line) for line in lines]
    text = "\n".join(lines)
    return text


def _grade_answers(answers):
    counter = 0
    for key in answers.keys():
        expected_answer, computed_answer = answers[key]
        expected_answer = _format_text(expected_answer)
        computed_answer = _format_text(computed_answer)
        if computed_answer == expected_answer:
            counter += 1
        else:
            print("---< " + str(key) + " >" + "-" * 50)
            print("Expected:")
            print(repr(expected_answer))
            print("Computed:")
            print(repr(computed_answer))

    if len(answers.keys()) == 0:
        return 0.0
    return 5.0 * counter / len(answers.keys())


def _grade_notebook(filename):
    answers = _extract_answers_from_notebook(filename)
    # print(repr(answers))
    grade = _grade_answers(answers)
    return grade


def _main():
    files = [f for f in glob("*.ipynb")]
    grade = 0
    for file in files:
        print("File: " + file)
        grade += _grade_notebook(file)
    print(round(grade / len(files), 2))


#
# Main program
#
_main()
