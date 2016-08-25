import base64
import json
import logging
import math
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from app_user.models import AppUser
from app_api.api_util import compose_json_response

@csrf_exempt
def user_register(request):
	
	logger.info('user_register')
	try:
		body_unicode = request.body.decode('utf-8')
		body_data = json.loads(body_unicode)
		email = body_data['email']
	except Exception as exc:
		logger.error(exc)
		return compose_json_response(0, 'Required fields not provided', {})

	# Check that account does not already exist
	try:
		user = User.objects.get(email=email)
		return_data = {}
		return compose_json_response(0, 'This account already exists.', return_data)

	# Create Account
	except User.DoesNotExist:

		user = User()
		user.email = email
		user.username = body_data['userName']
		user.password = body_data['password']
		user.save()

		app_user = AppUser()
		app_user.logon_credentials = user
		app_user.device_id = body_data['deviceType'] if 'deviceType' in body_data else ''
		app_user.device_token = body_data['deviceToken'] if 'deviceToken' in body_data else ''
		app_user.save()

		# Process profile image if exist
		if 'image' in body_data and len(body_data['image']) > 2:
			image_data = base64.b64decode(body_data['image'])
			app_user.profile_image.save('profile.png', ContentFile(image_data), save=True)
			app_user.save()

		return_data = {'userID': app_user.id, 'rank': ''}

		return compose_json_response(200, 'Your account has been created successfully', return_data)


@csrf_exempt
def login(request):

	logger.info('login')
	try:
		body_unicode = request.body.decode('utf-8')
		body_data = json.loads(body_unicode)
		username = body_data['usernameEmail']
		password = body_data['password']

	except Exception as exc:
		logger.error(exc)
		return compose_json_response(0, 'Required fields not provided', {})

	user = authenticate(username=username, password=password) # returns Django model User

	if user is not None:
		app_user = user.app_user # Convert Django User model to instance of User (in this case AppUser)
		app_user.device_id = body_data['deviceType'] if 'deviceType' in body_data else ''
		app_user.device_token = body_data['deviceToken'] if 'deviceToken' in body_data else ''
		app_user.save()

		if user.is_active:
			auth_login(request, user) # Login requires Django User
		else:
			return compose_json_response(0, 'account not active, please contact administrator', {})
	else:
		return compose_json_response(0, 'please enter a valid username and password', {})

	return_data = {'userID': app_user.id, 'paid': app_user.paid_for_no_ads, 'rank': app_user.rank, 'isAdmin': app_user.is_admin}

	return compose_json_response(200, 'User login successfully.', return_data)


@csrf_exempt
def forgot_password(request):
	
	logger.info('forgot_password')
	try:
		body_unicode = request.body.decode('utf-8')
		body_data = json.loads(body_unicode)
		email = body_data['email']
	except Exception as exc:
		logger.error(exc)
		return compose_json_response(0, 'Required fields not provided', {})

	import random
	alphabet = "abcdefghijklmnopqrstuvwxyz"
	pw_length = 8
	mypw = ""

	for i in range(pw_length):
		next_index = random.randrange(len(alphabet))
		mypw = mypw + alphabet[next_index]

	# replace 1 or 2 characters with a number
	for i in range(random.randrange(1,3)):
		replace_index = random.randrange(len(mypw)//2)
		mypw = mypw[0:replace_index] + str(random.randrange(10)) + mypw[replace_index+1:]

	# replace 1 or 2 letters with an uppercase letter
	for i in range(random.randrange(1,3)):
		replace_index = random.randrange(len(mypw)//2,len(mypw))
		mypw = mypw[0:replace_index] + mypw[replace_index].upper() + mypw[replace_index+1:]
	try:
		user = User.objects.get(email=email)
		user.password = mypw
		user.save()
	except User.DoesNotExist:
		return compose_json_response(0, 'Could not find user with this email', {})

	# email to user with new temporary password
	try:
		send_mail(
		    'Password Reset',
		    "We've reset your password to the following: %s," % mypw,
		    settings.DEFAULT_FROM_EMAIL,
		    ['%s' % user.email],
		    fail_silently=False,
		)
	except Exception as e:
		logging.error(e)

	return_data = {'pass': mypw}

	return compose_json_response(200, 'Your password sent on your registered Email ID.', return_data)	
