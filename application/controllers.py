# Importing necessary libraries
from flask import current_app as app
from flask import request, jsonify, render_template, redirect, url_for
from datetime import datetime
from app import db