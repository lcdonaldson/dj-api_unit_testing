class ApiTestCase(TestCase):
	def setUp(self):
		self.user = User()
		self.user.username = "user@test.com"
		self.user.email = "user@test.com"
		self.user.set_password('password')
		self.user.save()

		self.app_user = AppUser(logon_credentials=self.user)
		self.app_user.first_name = "tod"
		self.app_user.last_name = "zarnackey"
		self.app_user.bio = "gammer"
		self.app_user.website_url = "http://www.gamefly.com"
		self.app_user.facebook_url = "https://www.facebook.com/tod.zarnacky.32"
		self.app_user.pinterest_url = "https://www.pinterest.com"
		self.app_user.twitter_url = "https://www.twitter.com"
		self.app_user.save()
		
		# ============================  END USER  ================================

		# Create User 2
		self.user2 = User()
		self.user2.username = "number2@test.com"
		self.user2.email = "pennygetyourownwifi@yahoo.com"
		self.user2.set_password('asdfj')
		self.user2.save()

		self.app_user2 = AppUser(logon_credentials=self.user2)
		self.app_user2.first_name = "sheldon"
		self.app_user2.last_name = "cooper"
		self.app_user2.bio = "physicist"
		self.app_user2.website_url = "http://www.sheldoncooper.com"
		self.app_user2.facebook_url = "https://www.facebook.com/sheldon.cooper.7"
		self.app_user2.pinterest_url = "https://www.pinterest.com"
		self.app_user2.twitter_url = "https://www.twitter.com"
		self.app_user2.save()

		# ============================  END USER2  ================================

		# Create User 3
		self.user3 = User()
		self.user3.username = "thrice@test.com"
		self.user3.email = "lovemycat@yahoo.com"
		self.user3.set_password('abc1234')
		self.user3.save()

		self.app_user3 = AppUser(logon_credentials=self.user3)
		self.app_user3.first_name = "stuart"
		self.app_user3.last_name = "bloom"
		self.app_user3.bio = "small business owner"
		self.app_user3.website_url = "http://www.pasedenacomics.com"
		self.app_user3.facebook_url = "https://www.facebook.com/stuart.bloom.15"
		self.app_user3.pinterest_url = "https://www.pinterest.com"
		self.app_user3.twitter_url = "https://www.twitter.com"
		self.app_user3.save()

		# ============================  END USER3  ================================

					    # FOLLOWING CASES
					
		# Following
		self.following = OwnerFollow(following=self.app_user2, follower=self.app_user)
		self.following.save()

		# Following
		self.following = OwnerFollow(following=self.app_user3, follower=self.app_user)
		self.following.save()

		# Following
		self.following = OwnerFollow(following=self.app_user, follower=self.app_user2)
		self.following.save()

		# Following
		self.following = OwnerFollow(following=self.app_user3, follower=self.app_user2)
		self.following.save()

		# Following
		self.following = OwnerFollow(following=self.app_user, follower=self.app_user3)
		self.following.save()

		# Following
		self.following = OwnerFollow(following=self.app_user2, follower=self.app_user3)
		self.following.save()
		
	def testUserRegister(self):
		client = Client()

		post_params = {'userName': 'testuser', 'email': 'test@test.com', 'password': 'mypassword', 'deviceType': 'test',
		               'deviceToken': 'NA', 'image': string_encoded_image}
		response = client.post(reverse('app_api.views.user_register'), data=json.dumps(post_params), content_type='application/json')
		json_data = response.json()
		self.assertTrue(json_data['responseCode'] == 200)

		member = json_data['userID']
		person = AppUser.objects.get(id=member)
		self.assertTrue(person.email == 'test@test.com')

		response = client.post(reverse('app_api.views.user_register'), data=json.dumps(post_params), content_type='application/json')
		json_data = response.json()
		self.assertTrue(json_data['responseCode'] == 0)
		
	def testLogin(self):
		client = Client()

		post_params = {'usernameEmail': 'user@test.com', 'password': 'password', 'deviceType': 'test', 'deviceToken': 'asd123'}
		response = client.post(reverse('app_api.views.login'), data=json.dumps(post_params), content_type='application/json')
		json_data = response.json()
		self.assertTrue(json_data['responseCode'] == 200)

		member = json_data['userID']
		person = AppUser.objects.get(logon_credentials=member)
		self.assertTrue(person.device_token == 'asd123')
	
	def testForgotPassword(self):
		client = Client()

		post_params = {'email': self.user.email}
		# Checkout
		response = client.post(reverse('app_api.views.forgot_password'), data=json.dumps(post_params), content_type='application/json')
		json_data = response.json()
		self.assertTemplateNotUsed(json_data['responseCode'] == 200)
		self.assertTrue(json_data['responseCode'] == 200)

		# Three proofs of email working. mail.outbox is only for testing purposes.
		see = mail.outbox[0].to
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].subject, 'Password Reset')

		
# ****************** New Classs to test ************************

class ListCreateCourse(generics.ListCreateAPIView):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
