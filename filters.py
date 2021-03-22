from app import app
from flask import g


@app.template_filter()
def currency(value):
    curVal = float(value)
    return "${:,.2f}".format(curVal)


@app.template_filter()
def gbp(value):
    curVal = float(value) * g.gbp_rate
    return "${:,.2f}".format(curVal)
