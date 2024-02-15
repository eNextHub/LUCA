import re

def equation_separator(equation):

    counter = 0
    holder = []
    for c,s in enumerate(equation):
        if s in ("*/+-"):

            holder.extend(
                [f"[{equation[counter:c]}]" , s]
            )

            counter = c+1

    if not holder:
        return [f"[{equation}]"]

    return holder

def operator_sperator(equation):

    return [i  for i in ("*/+-") if i in equation]