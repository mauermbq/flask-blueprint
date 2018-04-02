"""
Translation module.
Actually it supports MS transaltion API only.
"""
import json
import requests # HTTP client for python
from flask_babel import _
from flask import current_app


def translate(text, source_language, dest_language):
    """
    This function translate submitted text via Microsoft Translator API.
    Take care that  MS_TRANSLATOR_KEY is set inyour environment.
    ----------
    text : str
        text to be translated
    source_language : str
        source language as language code
    destination_language : str
        destination language as language code
    Returns
    -------
    str
        translated text
    """
    # check if access key is set in your env
    if 'MS_TRANSLATOR_KEY' not in current_app.config or \
            not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    auth = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY']}
    # send HTTP GET request
    req = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
                       '/Translate?text={}&from={}&to={}'.format(
                           text, source_language, dest_language),
                       headers=auth)
    if req.status_code != 200:
        return _('Error: the translation service failed.')
    # decode via json.loads() into a Python string and return it
    return json.loads(req.content.decode('utf-8-sig'))
