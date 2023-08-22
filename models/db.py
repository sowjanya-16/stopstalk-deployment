# -*- coding: utf-8 -*-
"""
    Copyright (c) 2015-2020 Raj Patel(raj454raj@gmail.com), StopStalk

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

import json as json_for_views
import re

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Mail

## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    mysql_connection = 'mysql://' + current.mysql_user + \
                       ':' + current.mysql_password + \
                       '@' + current.mysql_server

    db = DAL(mysql_connection + '/' + current.mysql_dbname,
             table_hash="stopstalkdb")
    uvadb = DAL(mysql_connection + '/' + current.mysql_uvadbname,
                table_hash="uvajudge")

#    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*']
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

import datetime

import utilities
from gluon.tools import Auth, AuthJWT, PluginManager, Service
from stopstalk_constants import *

auth = Auth(db)
auth_jwt = AuthJWT(auth, secret_key=current.jwt_secret, user_param="email")
service = Service()
plugins = PluginManager()

all_countries = {u'Canada': u'CA', u'Moldova (Republic of)': u'MD', u'Sao Tome and Principe': u'ST', u'Guinea-Bissau': u'GW', u'United States of America': u'US', u'Lithuania': u'LT', u'Cambodia': u'KH', u'Saint Helena, Ascension and Tristan da Cunha': u'SH', u'Switzerland': u'CH', u'Ethiopia': u'ET', u'Aruba': u'AW', u'Saint Martin (French part)': u'MF', u'Solomon Islands': u'SB', u'Argentina': u'AR', u'Cameroon': u'CM', u'Burkina Faso': u'BF', u'Turkmenistan': u'TM', u'Ghana': u'GH', u'Saudi Arabia': u'SA', u'Rwanda': u'RW', u'Togo': u'TG', u'Japan': u'JP', u'American Samoa': u'AS', u'United States Minor Outlying Islands': u'UM', u'Cocos (Keeling) Islands': u'CC', u'Pitcairn': u'PN', u'Guatemala': u'GT', u'Bosnia and Herzegovina': u'BA', u'Kuwait': u'KW', u'Russian Federation': u'RU', u'Jordan': u'JO', u'Bonaire, Sint Eustatius and Saba': u'BQ', u'Dominica': u'DM', u'Liberia': u'LR', u'Maldives': u'MV', u'Jamaica': u'JM', u'Oman': u'OM', u'Martinique': u'MQ', u'Cabo Verde': u'CV', u'Christmas Island': u'CX', u'French Guiana': u'GF', u'Niue': u'NU', u'Monaco': u'MC', u'Wallis and Futuna': u'WF', u'New Zealand': u'NZ', u'Yemen': u'YE', u'Jersey': u'JE', u'Andorra': u'AD', u'Albania': u'AL', u'Samoa': u'WS', u'Norfolk Island': u'NF', u'United Arab Emirates': u'AE', u'Guam': u'GU', u'India': u'IN', u'Azerbaijan': u'AZ', u'Lesotho': u'LS', u'Saint Vincent and the Grenadines': u'VC', u'Kenya': u'KE', u'Macao': u'MO', u'Turkey': u'TR', u'Afghanistan': u'AF', u'Virgin Islands (British)': u'VG', u'Bangladesh': u'BD', u'Mauritania': u'MR', u'Congo (Democratic Republic of the)': u'CD', u'Turks and Caicos Islands': u'TC', u'Saint Lucia': u'LC', u'San Marino': u'SM', u'French Polynesia': u'PF', u'France': u'FR', u'Svalbard and Jan Mayen': u'SJ', u'Syrian Arab Republic': u'SY', u'Bermuda': u'BM', u'Slovakia': u'SK', u'Somalia': u'SO', u'Peru': u'PE', u'Swaziland': u'SZ', u'Nauru': u'NR', u'Seychelles': u'SC', u'Norway': u'NO', u'Malawi': u'MW', u'Cook Islands': u'CK', u'Benin': u'BJ', u'Western Sahara': u'EH', u'Cuba': u'CU', u'Montenegro': u'ME', u'Falkland Islands (Malvinas)': u'FK', u'Mayotte': u'YT', u'Heard Island and McDonald Islands': u'HM', u'China': u'CN', u'Armenia': u'AM', u'Timor-Leste': u'TL', u'Dominican Republic': u'DO', u'Bolivia (Plurinational State of)': u'BO', u'Ukraine': u'UA', u'Bahrain': u'BH', u'Tonga': u'TO', u'Finland': u'FI', u'Libya': u'LY', u'Macedonia (the former Yugoslav Republic of)': u'MK', u'Cayman Islands': u'KY', u'Central African Republic': u'CF', u'New Caledonia': u'NC', u'Mauritius': u'MU', u'Tajikistan': u'TJ', u'Liechtenstein': u'LI', u'Australia': u'AU', u'Mali': u'ML', u'Sweden': u'SE', u'Bulgaria': u'BG', u'Palestine, State of': u'PS', u"Korea (Democratic People's Republic of)": u'KP', u'Romania': u'RO', u'Angola': u'AO', u'French Southern Territories': u'TF', u'Chad': u'TD', u'South Africa': u'ZA', u'Tokelau': u'TK', u'Cyprus': u'CY', u'South Georgia and the South Sandwich Islands': u'GS', u'Brunei Darussalam': u'BN', u'Qatar': u'QA', u'Malaysia': u'MY', u'Austria': u'AT', u'Mozambique': u'MZ', u'Uganda': u'UG', u'Hungary': u'HU', u'Niger': u'NE', u'Isle of Man': u'IM', u'Brazil': u'BR', u'Virgin Islands (U.S.)': u'VI', u'Faroe Islands': u'FO', u'Guinea': u'GN', u'Panama': u'PA', u'Guyana': u'GY', u'Costa Rica': u'CR', u'Luxembourg': u'LU', u'Bahamas': u'BS', u'Gibraltar': u'GI', u'Ireland': u'IE', u'Pakistan': u'PK', u'Palau': u'PW', u'Nigeria': u'NG', u'Ecuador': u'EC', u'Czech Republic': u'CZ', u'Viet Nam': u'VN', u'Belarus': u'BY', u'Vanuatu': u'VU', u'Algeria': u'DZ', u'Slovenia': u'SI', u'El Salvador': u'SV', u'Tuvalu': u'TV', u'Saint Pierre and Miquelon': u'PM', u'Iran (Islamic Republic of)': u'IR', u'Marshall Islands': u'MH', u'Chile': u'CL', u'Puerto Rico': u'PR', u'Belgium': u'BE', u'Kiribati': u'KI', u'Haiti': u'HT', u'Belize': u'BZ', u'Hong Kong': u'HK', u'Sierra Leone': u'SL', u'Georgia': u'GE', u"Lao People's Democratic Republic": u'LA', u'Gambia': u'GM', u'Philippines': u'PH', u'Morocco': u'MA', u'Croatia': u'HR', u'Mongolia': u'MN', u'Guernsey': u'GG', u'Thailand': u'TH', u'Namibia': u'NA', u'Grenada': u'GD', u'Taiwan, Province of China': u'TW', u'Aland Islands': u'AX', u'Venezuela (Bolivarian Republic of)': u'VE', u'Iraq': u'IQ', u'Tanzania, United Republic of': u'TZ', u'Portugal': u'PT', u'Estonia': u'EE', u'Uruguay': u'UY', u'Equatorial Guinea': u'GQ', u'Lebanon': u'LB', u'Korea (Republic of)': u'KR', u'Uzbekistan': u'UZ', u'Tunisia': u'TN', u'Djibouti': u'DJ', u'Greenland': u'GL', u'Antigua and Barbuda': u'AG', u'Spain': u'ES', u'Colombia': u'CO', u'Burundi': u'BI', u'Fiji': u'FJ', u'Barbados': u'BB', u'Madagascar': u'MG', u'Italy': u'IT', u'Bhutan': u'BT', u'Sudan': u'SD', u'Nepal': u'NP', u'Malta': u'MT', u'Netherlands': u'NL', u'Northern Mariana Islands': u'MP', u'Suriname': u'SR', u'United Kingdom of Great Britain and Northern Ireland': u'GB', u'Anguilla': u'AI', u'Republic of Kosovo': u'XK', u'Micronesia (Federated States of)': u'FM', u'Holy See': u'VA', u'Israel': u'IL', u'Reunion': u'RE', u'Indonesia': u'ID', u'Iceland': u'IS', u'Zambia': u'ZM', u'Senegal': u'SN', u'Papua New Guinea': u'PG', u'Saint Kitts and Nevis': u'KN', u'Trinidad and Tobago': u'TT', u'Zimbabwe': u'ZW', u'Germany': u'DE', u'Denmark': u'DK', u'Kazakhstan': u'KZ', u'Poland': u'PL', u'Eritrea': u'ER', u'Kyrgyzstan': u'KG', u'Saint Barthelemy': u'BL', u'British Indian Ocean Territory': u'IO', u'Montserrat': u'MS', u'Mexico': u'MX', u'Sri Lanka': u'LK', u'Latvia': u'LV', u'South Sudan': u'SS', u'Curacao': u'CW', u'Guadeloupe': u'GP', u"Cote d'Ivoire": u'CI', u'Honduras': u'HN', u'Myanmar': u'MM', u'Bouvet Island': u'BV', u'Egypt': u'EG', u'Nicaragua': u'NI', u'Singapore': u'SG', u'Serbia': u'RS', u'Botswana': u'BW', u'Antarctica': u'AQ', u'Congo': u'CG', u'Sint Maarten (Dutch part)': u'SX', u'Greece': u'GR', u'Paraguay': u'PY', u'Gabon': u'GA', u'Comoros': u'KM'}
reverse_country_mapping = dict(map(lambda x: (x[1], x[0]),
                                   all_countries.items()))
current.all_countries = all_countries
country_name_list = all_countries.keys()
country_name_list.sort()

# To disable writing of translations
# http://www.web2py.com/books/default/chapter/29/04#Translating-variables
T.is_writable = False

initial_date = datetime.datetime.strptime(current.INITIAL_DATE, "%Y-%m-%d %H:%M:%S")

db.define_table("institutes",
                Field("name", label=T("Name")))

itable = db.institutes
all_institutes = db(itable).select(itable.name,
                                   orderby=itable.name)
all_institutes = [x["name"].strip("\"") for x in all_institutes]
all_institutes.append("Other")
extra_fields = [Field("institute",
                      label=T("Institute"),
                      requires=IS_IN_SET(all_institutes,
                                         zero=T("Institute"),
                                         error_message=T("Institute required")),
                      comment=T("Write to us if your Institute is not listed")),
                Field("country",
                      label=T("Country"),
                      requires=IS_IN_SET(country_name_list,
                                         zero=T("country"),
                                         error_message=T("Country required")),
                      comment=T("Write to us if your Country is not listed"),
                      default=""),
                Field("stopstalk_handle",
                      label=T("StopStalk handle"),
                      requires=[IS_NOT_EMPTY(error_message=auth.messages.is_empty),
                                IS_NOT_IN_DB(db,
                                             "auth_user.stopstalk_handle",
                                             error_message=T("Handle taken")),
                                IS_NOT_IN_DB(db,
                                             "custom_friend.stopstalk_handle",
                                             error_message=T("Handle taken"))],
                      comment=T("Unique handle to identify distinctly on StopStalk")),
                Field("rating",
                      default=0,
                      writable=False),
                Field("prev_rating",
                      default=0,
                      writable=False),
                Field("stopstalk_rating", "integer",
                      default=0,
                      writable=False),
                Field("stopstalk_prev_rating", "integer",
                      default=0,
                      writable=False),
                Field("per_day", "double",
                      default=0.0,
                      writable=False),
                Field("per_day_change",
                      default="0.0",
                      writable=False),
                Field("referrer",
                      label=T("Referrer's StopStalk Handle"),
                      default="",
                      comment=T("StopStalk handle of a verified user")),
                Field("allowed_cu", "integer",
                      default=3,
                      readable=False,
                      writable=False),
                Field("blacklisted", "boolean",
                      default=False,
                      readable=False,
                      writable=False),
                Field("authentic", "boolean",
                      default=False,
                      readable=False,
                      writable=False),
                Field("graph_data_retrieved", "boolean",
                      default=False,
                      readable=False,
                      writable=False),
                Field("refreshed_timestamp",
                      "datetime",
                      default=initial_date,
                      writable=False)]

site_handles = []
all_last_retrieved = []
for site in current.SITES:
    site_handles.append(Field(site.lower() + "_handle",
                              label=site + " handle"))
    all_last_retrieved.append(Field(site.lower() + "_lr", "datetime",
                                    default=initial_date,
                                    writable=False))

extra_fields += site_handles
extra_fields += all_last_retrieved
auth.settings.extra_fields["auth_user"] = extra_fields
auth.settings.logging_enabled = False

auth.define_tables(username=False, signature=False)

## configure email

# Normal mails go through contactstopstalk@gmail.com
mail = auth.settings.mailer
mail.settings.server = current.smtp_server
mail.settings.sender = "Team StopStalk <" + current.sender_mail + ">"
mail.settings.login = current.sender_mail + ":" + current.sender_password

# Bulk emails go through admin@stopstalk.com
bulkmail = Mail()
bulkmail.settings.server = current.bulk_smtp_server
bulkmail.settings.sender = "Team StopStalk <" + current.bulk_sender_mail + ">"
bulkmail.settings.login = current.bulk_sender_user + ":" + current.bulk_sender_password

from influxdb import InfluxDBClient
from redis import Redis

# REDIS CLIENT
current.REDIS_CLIENT = Redis(host=current.redis_server, port=current.redis_port, db=0)

# INFLUX CLIENT
current.INFLUXDB_CLIENT = InfluxDBClient(current.influxdb_server,
                                         current.influxdb_port,
                                         current.influxdb_user,
                                         current.influxdb_password,
                                         INFLUX_DBNAME)


# -----------------------------------------------------------------------------
def send_mail(to, subject, message, mail_type, bulk=False):
    """
        Email sending helper wrapper around Web2Py Mailer

        @param to (String): Recipient of the mail
        @param subject (String): Subject of the mail
        @param message (String): Message body of the mail
        @param mail_type (String): Mail type (used for handling subscriptions)
        @param bulk (Boolean): Bulk sending mail
    """

    # Check if user has unsubscribed from email updates
    utable = db.unsubscriber

    query = (utable.email == to)
    if mail_type != "admin":
        query &= (utable[mail_type] == False)

    row = db(query).select().first()

    if row is None or mail_type == "admin":
        if bulk:
            db.queue.insert(status="pending",
                            email=to,
                            subject=subject,
                            message=message)
        else:
            bulkmail.send(to=to,
                          subject=subject,
                          message=message)

current.send_mail = send_mail
## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.reset_password_requires_verification = True
auth.settings.formstyle = utilities.materialize_form
auth.settings.login_next = URL("default", "index")

auth.messages.email_sent = T("Verification Email sent")
auth.messages.logged_out = T("Successfully logged out")
auth.messages.invalid_login = T("Invalid login credentials")
auth.messages.label_remember_me = T("Remember credentials")
auth.settings.long_expiration = 3600 * 24 * 60 # Remember me for two months

# -----------------------------------------------------------------------------
def validate_email(email):
    """
        Check if an email is from a valid domain name

        @param email (String): Email address
        @return (Boolean): Valid email or not
    """

    if email.strip() == "":
        return False

    if email.__contains__(".ac.in"):
        return True

    import requests

    def _fallback_email_validation(email):
        """
            Called in the following cases

            1. access_key is empty or not mentioned in 0firstrun.py
            2. Network failure for NeverBounce API
        """
        domain = email.split("@")[-1]
        try:
            response = requests.get("http://" + domain,
                                    headers={"User-Agent": COMMON_USER_AGENT},
                                    timeout=3)
            return (response.status_code == 200)
        except:
            return False

    attable = db.access_tokens
    query = (attable.time_stamp > (datetime.datetime.now() - \
                                   datetime.timedelta(minutes=55))) & \
            (attable.type == "NeverBounce access_token")
    row = db(query).select(orderby="<random>").first()
    if row:
        access_token = row.value
    else:
        return _fallback_email_validation(email)

    response = requests.post("https://api.neverbounce.com/v3/single",
                             data={"access_token": access_token,
                                   "email": email})
    if response.status_code == 200:
        response = response.json()
        if response["success"]:
            return (response["result"] not in (1, 4))
        else:
            return _fallback_email_validation(email)
    else:
        return _fallback_email_validation(email)

# -----------------------------------------------------------------------------
def sanitize_fields(form):
    """
        Display errors for the following:

        1.  Strip whitespaces from all the fields
        2.  Remove @ from the HackerEarth
        3.  Lowercase the handles
        4.  Fill the institute field with "Other" if empty
        5.  Email address entered is from a valid domain
        6.  Email address instead of handles
        7.  Spoj follows a specific convention for handle naming
        8.  stopstalk_handle is alphanumeric
        9.  Country field is compulsory
        10. Only positive ints allowed in Timus field
        11. HackerRank handle should not be containing hr_r=1

        @param form (FORM): Registration / Add Custom friend form
    """

    from re import match

    if form.vars.stopstalk_handle:
        # 8.
        if not utilities.is_valid_stopstalk_handle(form.vars.stopstalk_handle):
            form.errors.stopstalk_handle = T("Expected alphanumeric (Underscore allowed)")

    def _remove_at_symbol(site_name):
        if site_name in current.SITES:
            field = site_name.lower() + "_handle"
            if form.vars[field] and form.vars[field][0] == "@":
                form.errors[field] = T("@ symbol not required")

    def _valid_spoj_handle(handle):
        try:
            return match("[a-z]+[0-9a-z_]*", handle).group() == handle
        except AttributeError:
            return False

    handle_fields = ["stopstalk"]
    handle_fields.extend([x.lower() for x in current.SITES.keys()])

    # 1, 6 and 11
    for field in handle_fields:
        field_handle = field + "_handle"
        if form.vars[field_handle]:
            if field != "uva" and form.vars[field_handle].__contains__(" "):
                form.errors[field_handle] = T("White spaces not allowed")
            elif IS_EMAIL(error_message="check")(form.vars[field_handle])[1] != "check":
                form.errors[field_handle] = T("Email address instead of handle")
            elif field == "hackerrank" and form.vars[field_handle].__contains__("hr_r=1"):
                form.errors[field_handle] = T("Please enter only the handle")

            if form.vars[field_handle].__contains__("http:") or \
                 form.vars[field_handle].__contains__("https:") or \
                 form.vars[field_handle].__contains__("www.") or \
                 form.vars[field_handle].__contains__("codechef.com") or \
                 form.vars[field_handle].__contains__("codeforces.com") or \
                 form.vars[field_handle].__contains__("hackerearth.com") or \
                 form.vars[field_handle].__contains__("hackerrank.com"):
                form.errors[field_handle] = T("Please enter only the handle")

    # 2.
    _remove_at_symbol("HackerEarth")

    # 7.
    if "Spoj" in current.SITES:
        if form.vars["spoj_handle"] and \
           not _valid_spoj_handle(form.vars["spoj_handle"]):
            form.errors["spoj_handle"] = T("Handle should only contain lower case letters 'a'-'z', underscores '_', digits '0'-'9', and must start with a letter!")

    # 3.
    for site in handle_fields:
        site_handle = site + "_handle"
        if site in ["hackerrank", "uva", "stopstalk", "atcoder"]:
            continue
        if form.vars[site_handle] and \
           form.vars[site_handle] != form.vars[site_handle].lower():
            form.vars[site_handle] = form.vars[site_handle].lower()

    # 4.
    if form.vars.institute == "":
        form.errors.institute = T("Please select an institute or Other")

    # 9.
    if form.vars.country == "":
        form.errors.country = T("Country required")

    # 5.
    if form.vars.email:
        if validate_email(form.vars.email) is False:
            form.errors.email = T("Invalid email address")

    # 10.
    if form.vars.timus_handle:
        try:
            timus_id = int(form.vars.timus_handle)
            if timus_id <= 0:
                form.errors.timus_handle = "Timus handle / ID should be a number"
        except ValueError:
            form.errors.timus_handle = "Timus handle / ID should be a number"

    if form.errors:
        response.flash = T("Form has errors")

#-----------------------------------------------------------------------------
def notify_institute_users(record):
    """
        Send mail to all users from the same institute
        when a user registers from that institute (after email verification)

        @param record (Row): Record having the user details
    """

    # Skip inserting into database
    return
    new_user_has_atleast_one_handle = any([record[site.lower() + "_handle"] for site in current.SITES])
    if not new_user_has_atleast_one_handle:
        return

    atable = db.auth_user
    iutable = db.institute_user
    query = (atable.institute == record.institute) & \
            (atable.email != record.email) & \
            (atable.country == record.country) & \
            (atable.institute != "Other") & \
            (atable.blacklisted == False) & \
            (atable.registration_key == "")

    atleast_one_handle_query = False
    for site in current.SITES:
        atleast_one_handle_query |= (atable[site.lower() + "_handle"] != "")

    query &= atleast_one_handle_query

    rows = db(query).select(atable.id)

    if len(rows):
        for row in rows:
            iutable.insert(send_to_id=row.id,
                           user_registered_id=record.id)
            db.commit()

def create_next_retrieval_record(record, custom=False):
    """
        Create a record corresponding to the new user

        @param record (Row): Record with the new user details
        @param custom (Boolean): If the user is a custom user
    """
    if custom:
        db.next_retrieval.insert(custom_user_id=record.id)
    else:
        db.next_retrieval.insert(user_id=record.id)

    keyname = utilities.get_codechef_last_retrieved_key(record.id, custom)
    current.REDIS_CLIENT.set(keyname, current.INITIAL_DATE)

def append_user_to_refreshed_users(record):
    """
        Add the user in refreshed list to retrieve submissions asap

        @param record (Row): Record with the new user details
    """
    current.REDIS_CLIENT.rpush("next_retrieve_user", record.id)

# -----------------------------------------------------------------------------
def register_callback(form, register_type="normal"):
    """
        Send mail to raj454raj@gmail.com about all the users who register

        @param form (FORM): Register form
    """

    site_handles = []
    for site in current.SITES:
        site_handles.append(site)
    # Send mail to raj454raj@gmail.com
    to = "raj454raj@gmail.com"
    subject = "New user registered"
    message = """
Name: %s %s
Email: %s
Register Type: %s
Institute: %s
Country: %s
StopStalk handle: %s
Referrer: %s\n""" % (form.vars.first_name,
                     form.vars.last_name,
                     form.vars.email,
                     register_type,
                     form.vars.institute,
                     form.vars.country,
                     form.vars.stopstalk_handle,
                     form.vars.referrer)

    for site in current.SITES:
        message += "%s handle: %s\n" % (site, form.vars[site.lower() + "_handle"])
    send_mail(to=to, subject=subject, message=message, mail_type="admin")

auth.settings.register_onvalidation = [sanitize_fields]
auth.settings.register_onaccept.append(register_callback)
auth.settings.verify_email_onaccept.extend([notify_institute_users,
                                            create_next_retrieval_record,
                                            append_user_to_refreshed_users])
current.auth = auth
current.auth_jwt = auth_jwt
current.response.formstyle = utilities.materialize_form
current.sanitize_fields = sanitize_fields
current.register_callback = register_callback
current.notify_institute_users = notify_institute_users
current.create_next_retrieval_record = create_next_retrieval_record
current.append_user_to_refreshed_users = append_user_to_refreshed_users

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

custom_friend_fields = [Field("user_id", "reference auth_user"),
                        Field("first_name",
                              label=T("First Name"),
                              requires=IS_NOT_EMPTY()),
                        Field("last_name",
                              label=T("Last Name"),
                              requires=IS_NOT_EMPTY()),
                        Field("institute",
                              label=T("Institute"),
                              requires=IS_IN_SET(all_institutes,
                                                 zero=T("Institute")),
                              comment=T("Write to us if your Institute is not listed")),
                        Field("country",
                              label=T("Country"),
                              requires=IS_IN_SET(country_name_list,
                                                 zero=T("country"),
                                                 error_message=T("Country required")),
                              comment=T("Write to us if your Country is not listed"),
                              default=""),
                        Field("stopstalk_handle",
                              label=T("StopStalk handle"),
                              requires=[IS_NOT_IN_DB(db,
                                                     "auth_user.stopstalk_handle",
                                                     error_message=T("Handle already exists")),
                                        IS_NOT_IN_DB(db,
                                                     "custom_friend.stopstalk_handle",
                                                     error_message=T("Handle already exists"))],
                              comment=T("Unique handle to identify distinctly on StopStalk")),
                        Field("rating",
                              default=0,
                              writable=False),
                        Field("prev_rating",
                              default=0,
                              writable=False),
                        Field("stopstalk_rating", "integer",
                              default=0,
                              writable=False),
                        Field("stopstalk_prev_rating", "integer",
                              default=0,
                              writable=False),
                        Field("per_day", "double",
                              default=0.0,
                              writable=False),
                        Field("per_day_change",
                              default="0.0",
                              writable=False),
                        Field("duplicate_cu", "reference custom_friend",
                              default=None),
                        Field("graph_data_retrieved", "boolean",
                              default=False,
                              readable=False,
                              writable=False),
                        Field("refreshed_timestamp",
                              "datetime",
                              default=initial_date,
                              writable=False)]

custom_friend_fields += site_handles
custom_friend_fields += all_last_retrieved
db.define_table("custom_friend",
                format="%(first_name)s %(last_name)s (%(id)s)",
                *custom_friend_fields)

def _count_users_lambda(row):
    if row.problem.user_ids in (None, ""):
        return 0
    else:
        return len(row.problem.user_ids) - \
               len(row.problem.user_ids.replace(",", "")) + 1

def _count_custom_users_lambda(row):
    if row.problem.custom_user_ids in (None, ""):
        return 0
    else:
        return len(row.problem.custom_user_ids) - \
               len(row.problem.custom_user_ids.replace(",", "")) + 1

db.define_table("problem",
                Field("name"),
                Field("link"),
                Field("tags", default="['-']"),
                Field("editorial_link", default=None),
                Field("tags_added_on", "date"),
                Field("editorial_added_on", "date"),
                Field("solved_submissions", "integer", default=0),
                Field("total_submissions", "integer", default=0),
                Field("user_ids", "text", default=""),
                Field("custom_user_ids", "text", default=""),
                Field("difficulty", "float"),
                Field.Virtual("user_count", _count_users_lambda),
                Field.Virtual("custom_user_count", _count_custom_users_lambda),
                format="%(name)s %(id)s")

db.define_table("submission",
                Field("user_id", "reference auth_user"),
                Field("custom_user_id", "reference custom_friend"),
                Field("stopstalk_handle"),
                Field("site_handle"),
                Field("site"),
                Field("time_stamp", "datetime"),
                Field("problem_id", "reference problem"),
                Field("problem_name"),
                Field("problem_link"),
                Field("lang"),
                Field("status"),
                Field("points"),
                Field("view_link",
                      default=""))

db.define_table("following",
                Field("user_id", "reference auth_user"),
                Field("follower_id", "reference auth_user"))

db.define_table("todays_requests",
                Field("user_id", "reference auth_user"),
                Field("follower_id", "reference auth_user"),
                Field("transaction_type"))

db.define_table("tag",
                Field("value"),
                format="%(value)s")

db.define_table("suggested_tags",
                Field("user_id", "reference auth_user"),
                Field("problem_id", "reference problem"),
                Field("tag_id", "reference tag"))

db.define_table("contact_us",
                Field("name", requires=IS_NOT_EMPTY()),
                Field("email", requires=[IS_NOT_EMPTY(), IS_EMAIL()]),
                Field("phone_number", requires=IS_NOT_EMPTY()),
                Field("subject", requires=IS_NOT_EMPTY()),
                Field("text_message", "text", requires=IS_NOT_EMPTY()))

db.define_table("institute_user",
                Field("send_to_id", "reference auth_user"),
                Field("user_registered_id", "reference auth_user"))

db.define_table("faq",
                Field("question", requires=IS_NOT_EMPTY()),
                Field("answer", requires=IS_NOT_EMPTY()))

db.define_table("stickers_given",
                Field("user_id", "reference auth_user"),
                Field("sticker_count", "integer"))

db.define_table("unsubscriber",
                Field("email",
                      requires=IS_EMAIL()),
                Field("feature_updates",
                      "boolean",
                      default=True,
                      label=T("New feature updates from StopStalk")),
                Field("institute_user",
                      "boolean",
                      default=True,
                      label=T("Notify when a user from your Institute registers")),
                Field("friend_unfriend",
                      "boolean",
                      default=True,
                      label=T("Notify when a user adds/removes me as a friend")),
                Field("time_stamp", "datetime"))

nr_fields = [Field("user_id", "reference auth_user"),
             Field("custom_user_id", "reference custom_friend")]

for site in current.SITES:
    nr_fields.append(Field(site.lower() + "_delay", "integer", default=0))

db.define_table("next_retrieval", *nr_fields)

site_fields = []
for site in current.SITES:
    site_fields.append(Field(site.lower(), "integer", default=0))

db.define_table("queue",
                Field("status"),
                Field("email"),
                Field("subject"),
                Field("message", "text"))

db.define_table("sessions_today",
                Field("message", "string"))

db.define_table("download_submission_logs",
                Field("user_id", "reference auth_user"),
                Field("url", "string"))

db.define_table("failed_retrieval",
                Field("user_id", "reference auth_user"),
                Field("custom_user_id", "reference custom_friend"),
                Field("site"))

db.define_table("invalid_handle",
                Field("handle"),
                Field("site"))

db.define_table("contest_logging",
                Field("click_type"),
                Field("contest_details", "text"),
                Field("stopstalk_handle"),
                Field("time_stamp", "datetime"))

db.define_table("http_errors",
                Field("status_code", "integer"),
                Field("content", "text"),
                Field("user_id", "reference auth_user"))

db.define_table("todo_list",
                Field("user_id", "reference auth_user"),
                Field("problem_link"))

db.define_table("access_tokens",
                Field("value"),
                Field("time_stamp", "datetime"),
                Field("type"))

db.define_table("testimonials",
                Field("user_id", "reference auth_user"),
                Field("content", "text"),
                Field("stars"),
                Field("verification", default="pending"),
                Field("created_at", "datetime"))

# facebook_group - Notify about the new Facebook group
db.define_table("recent_announcements",
                Field("user_id", "reference auth_user"),
                Field("data", "text", default="{}"))

db.define_table("user_editorials",
                Field("user_id", "reference auth_user"),
                Field("problem_id", "reference problem"),
                Field("added_on", "datetime"),
                Field("s3_key"),
                Field("votes", "text"),
                Field("verification", default="pending"))

db.define_table("resume_data",
                Field("user_id", "reference auth_user"),
                Field("resume_file_s3_path"),
                Field("will_relocate", "boolean"),
                Field("github_profile"),
                Field("linkedin_profile"),
                Field("join_from", "datetime"),
                Field("graduation_year"),
                Field("experience"),
                Field("fulltime_or_internship"),
                Field("contact_number"),
                Field("can_contact", "boolean"),
                Field("expected_salary"))

db.define_table("problem_difficulty",
                Field("user_id", "reference auth_user"),
                Field("problem_id", "reference problem"),
                Field("score", "integer", default=0))

db.define_table("problem_setters",
                Field("problem_id", "reference problem"),
                Field("handle"))

db.define_table("atcoder_problems",
                Field("problem_identifier"),
                Field("contest_id"),
                Field("name"))

db.define_table("problem_recommendations",
                Field("user_id", "reference auth_user"),
                Field("problem_id", "reference problem"),
                # The possible states of a recommendation are:
                # 0 - Recommended, 1 - Viewed, 2 - Attempted, 3 - Solved
                Field("state", "integer", default=0),
                Field("is_active", "boolean"),
                Field("generated_at", "date"))

uvadb.define_table("problem",
                   Field("problem_id", "integer"),
                   Field("problem_num", "integer"),
                   Field("title"),
                   Field("problem_status", "integer"))

uvadb.define_table("usernametoid",
                   Field("username"),
                   Field("uva_id"))

if session["auth"]:
    session["handle"] = session["auth"]["user"]["stopstalk_handle"]
    session["user_id"] = session["auth"]["user"]["id"]

current.db = db
current.uvadb = uvadb

current.WEIGHTING_FACTORS = {
    "curr_day_streak": 40 * 10,
    "max_day_streak": 20 * 10,
    "solved": 1 * 23,
    "accuracy": 5 * 35,
    "attempted": 2 * 2,
    "curr_per_day": 1000 * 20
}
current.REFRESH_INTERVAL = 120 * 60

# ----------------------------------------------------------------------------
def get_static_file_version(file_path):
    if current.environment == "production":
        new_file_path = file_path
        static_dir = "static/minified_files"
        if file_path[-3:] == ".js":
            new_file_path = file_path[:-3] + ".min.js"
        elif file_path[-4:] == ".css":
            new_file_path = file_path[:-4] + ".min.css"
        else:
            static_dir = "static"
            new_file_path = file_path
    else:
        new_file_path = file_path
        static_dir = "static"

    return static_dir, new_file_path, current.REDIS_CLIENT.get(new_file_path)

# ----------------------------------------------------------------------------
def get_static_url(file_path):
    """
        Get the link to the minified static file with versioning
        @params file_path (String): Relative path of the static file

        @return (String): URL of the minified static resource with versioning
    """

    if current.environment == "production":
        static_dir, file_path, revision = get_static_file_version(file_path)
        return URL(static_dir,
                   file_path,
                   vars={"_rev": revision},
                   extension=False)
    else:
        return URL("static",
                   file_path,
                   extension=False)

current.get_static_file_version = get_static_file_version
current.get_static_url = get_static_url

# =============================================================================
