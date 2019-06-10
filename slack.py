#! /usr/bin/env python3

import dcom

import configparser
import json
import requests

CONFIG_PATH = 'slack.conf'


def slack_message(uri, text):
    params = {'text': text}
    requests.post(uri, data=json.dumps(params))


if __name__ == '__main__':
    config = configparser.ConfigParser()
    with open(CONFIG_PATH) as conf_file:
        config.read_file(conf_file)
    uri = config["Slack"]["WebhookUri"]
    par = dcom.get_dcom_data(dcom.get_random_dcom())
    slack_message(uri, par)
