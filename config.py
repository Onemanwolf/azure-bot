#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MICROSOFT_APP_ID", "<<MICROSOFT-APP-ID>>") #"6bb6245f-400c-4e31-9473-e6dd60c96023"
    APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD", "<<MICROSOFT-APP-PASSWORD>>") #".hQ8Q~QOw8VZLRCgYkgHXkzMt2u_VhAA5Lxdic4W"
