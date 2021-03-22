import os
import requests
from flask import Flask, render_template, request, jsonify, g, json
from flask_sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

from models import Filer, Recipient
from filters import currency

namespaces = {'irs': 'http://www.irs.gov/efile'}

api_conversion = 'https://api.exchangeratesapi.io/latest?base=USD&symbols=GBP'


@app.before_request
def before_request_func():
    print("before_request is running!")
    r = requests.get(api_conversion)
    my_json = json.loads(r.content.decode('utf8').replace("'", '"'))
    g.gbp_rate = my_json["rates"]["GBP"]


@app.route('/filings', methods=[
    'GET',
])
def filings():
    return jsonify({
        'filers':
        list(map(lambda filer: filer.serialize(), Filer.query.all()))
    })


@app.route('/recipients', methods=[
    'GET',
])
@app.route('/recipients/<string:state>', methods=[
    'GET',
])
def recipients(state='ALL'):
    if state == 'ALL':
        return jsonify({
            'recipients':
            list(
                map(lambda recipient: recipient.serialize(),
                    Recipient.query.all()))
        })
    else:
        state = state.upper()
        return jsonify({
            'recipients':
            list(
                map(lambda recipient: recipient.serialize(),
                    Recipient.query.filter(Recipient.state == state).all()))
        })


@app.route('/xml', methods=['GET', 'POST'])
def xml():
    errors = []
    results = {}
    if request.method == "POST":
        try:
            url = request.form['url']
            r = requests.get(url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
            return render_template('index.html', errors=errors)
        if r:
            # xml processing
            root = ET.fromstring(r.content)
            results = parseXml(root)

    return render_template('index.html', errors=errors, results=results)


def parseXml(root):
    errors = []
    filers = root.findall('.//irs:Filer', namespaces=namespaces)
    filerEin = ''
    allRecipients = []
    allFilers = []
    for filer in filers:
        if filer != None:
            currentFiler = getFilerData(filer)
            if len(currentFiler['errors']) > 0:
                errors.append(currentFiler['errors'])
            filerEin = currentFiler['ein']
            allFilers.append(currentFiler)
    recipients = root.findall('.//irs:RecipientTable', namespaces=namespaces)
    for recipient in recipients:
        currentRecipient = getRecipientData(recipient, filerEin)
        allRecipients.append(currentRecipient)
        if len(currentRecipient['errors']) > 0:
            errors.append(currentRecipient['errors'])
    results = {
        'recipients': allRecipients,
        'filer': allFilers,
        'errors': errors
    }
    return results


def getFilerData(filer):
    errors = []
    filerObj = {}
    filerObj['ein'] = checkIfNone(filer.find('irs:EIN', namespaces=namespaces))
    filerObj['name'] = checkIfNone(
        filer.find('irs:Name/irs:BusinessNameLine1', namespaces=namespaces))
    address = getAddress(filer.find('irs:USAddress', namespaces=namespaces))
    filerObj['addressLine1'] = address['line1']
    filerObj['city'] = address['city']
    filerObj['state'] = address['state']
    filerObj['postalCode'] = address['postalCode']
    try:
        filerToAdd = Filer(filerObj['ein'], filerObj['name'],
                           filerObj['addressLine1'], filerObj['city'],
                           filerObj['state'], filerObj['postalCode'])
        db.session.add(filerToAdd)
        db.session.commit()
    except Exception as e:
        errors.append("Unable to add item to database.")
        errors.append(e)
        db.session.rollback()
    filerObj['errors'] = errors
    return filerObj


def getRecipientData(recipient, filerEin):
    errors = []
    recipientObj = {}
    recipientObj['ein'] = checkIfNone(
        recipient.find('irs:EINOfRecipient', namespaces=namespaces))
    recipientObj['name'] = checkIfNone(
        recipient.find('irs:RecipientNameBusiness/irs:BusinessNameLine1',
                       namespaces=namespaces))
    address = getAddress(recipient.find('irs:AddressUS',
                                        namespaces=namespaces))
    recipientObj['addressLine1'] = address['line1']
    recipientObj['city'] = address['city']
    recipientObj['state'] = address['state']
    recipientObj['postalCode'] = address['postalCode']
    recipientObj['amountOfCashGrant'] = checkIfNone(
        recipient.find('irs:AmountOfCashGrant', namespaces=namespaces))
    recipientObj['purposeOfGrant'] = checkIfNone(
        recipient.find('irs:PurposeOfGrant', namespaces=namespaces))
    try:
        recipientToAdd = Recipient(recipientObj['ein'], recipientObj['name'],
                                   recipientObj['addressLine1'],
                                   recipientObj['city'], recipientObj['state'],
                                   recipientObj['postalCode'], filerEin,
                                   recipientObj['amountOfCashGrant'],
                                   recipientObj['purposeOfGrant'])
        db.session.add(recipientToAdd)
        db.session.commit()
    except Exception as e:
        errors.append("Unable to add item to database.")
        errors.append(e)
        db.session.rollback()
    recipientObj['errors'] = errors
    return recipientObj


def getAddress(addressUS):
    address = {}
    address['line1'] = checkIfNone(
        addressUS.find('irs:AddressLine1', namespaces=namespaces))
    address['city'] = checkIfNone(
        addressUS.find('irs:City', namespaces=namespaces))
    address['state'] = checkIfNone(
        addressUS.find('irs:State', namespaces=namespaces))
    address['postalCode'] = checkIfNone(
        addressUS.find('irs:ZIPCode', namespaces=namespaces))
    return address


def checkIfNone(item):
    return item.text if item != None else None


if __name__ == '__main__':
    app.run()