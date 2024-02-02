#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MICROSOFT_APP_ID", "<<MICROSOFT-APP-ID>>")
    APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD", "<<MICROSOFT-APP-PASSWORD>>")
    BASE_URL = os.environ.get("BASE_URL", "<<BASE-URL>>")
    RATINGS_URL = os.environ.get("RATINGS_URL", "<<RATINGS-URL>>")