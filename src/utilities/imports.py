from flask import Flask, Blueprint, render_template,request, flash, make_response, Response,jsonify
from flask import current_app

# Login manager
from flask_login import LoginManager,login_required,fresh_login_required, current_user
import pytz

from config import config
#Instancia de DIDIPSA
#from config import DIDIPSA  
# Models
from models.ModelTablas import ModelTablas
from models.scaizen_cv_funtions import DailyReportFuntions,GeneralReport

# Entities
from models.entities.Tablas import *
from models.entities.Distribuidor.Complementos import Comp_Distribucion
from models.entities.Comercializador.Complementos import Comp_Comercializador
from config_carpet.config import GlobalConfig, clave_hex_hash, VerificarPermisosUsuario

#CLASESJSONXML
from models.entities.JSONXML import *
from models.ModelJSONXML import ModelJSONXML

#
from werkzeug.utils import secure_filename

#Evento
import datetime
import pytz
import logging #para registrar errores y eventos.
from models.scaizen_cv import EventosComercializador,EventosDistribuidor,EventosAlarmasDistribuidor

from models.scaizen_cv_funtions import DailyReportFuntions


# MySQL
#from flask_mysqldb import MySQL
from extensions import db
from flask_paginate import Pagination #Importando paquete de paginación

from flask import jsonify, redirect
from jsonschema import validate, ValidationError
from models import scaizen_cv as cv, scaizen_cv_funtions, scazen_datadb as scaizen_db
from utilities.mensual_report_files import PDF
import json
import hashlib

from flask import jsonify
from datetime import datetime, timedelta, timezone

#from wtforms import StringField, PasswordField, SubmitField, SelectField
#from wtforms.validators import DataRequired, Length, Email, Regexp
#from flask_wtf import FlaskForm
#from flask_wtf.recaptcha import RecaptchaField
from fpdf import FPDF
from lxml import etree
from lxml.etree import Element, SubElement, tostring
import xmlschema

import os
import xml.etree.ElementTree as ET
from pathlib import Path
import io
import calendar
import locale
from itertools import zip_longest
from models import scaizen_cv as cv
import logging
import traceback

from cryptography.fernet import Fernet

#Json manager
from data_json.managerjson import managerjson as mngj_son

#SqlAlchemy
from sqlalchemy import Numeric



logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(filename)s - line %(lineno)d : %(message)s'
)

def load_json_structure(file_path):
    """Lee la estructura JSON desde un archivo con codificación UTF-8."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


estructura_json_mensual_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","static/schemes/distribuidor/Mensual.schema.json"))
print(f"estructura_json_mensual_dir: {estructura_json_mensual_dir}")
estructura_json_mensual = load_json_structure(estructura_json_mensual_dir)

estructura_json_diario_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","static/schemes/distribuidor/Diario.schema.json"))
print(f"estructura_json_diario_dir: {estructura_json_diario_dir}")
estructura_json_diario = load_json_structure(estructura_json_diario_dir)