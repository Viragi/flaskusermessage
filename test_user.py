from app import app
import unittest


class MyAppIntegrationTestCase(unittest.TestCase):
    # get user list
    def test_userlist(self):
        client = app.test_client()
        result = client.get("/user")
        self.assertEqual(result.status_code, 200)
# get user add form

    def test_useraddform(self):
        client = app.test_client()
        result = client.get("/user/add")
        self.assertEqual(result.status_code, 200)
# get user add user

    def test_useradd(self):
        client = app.test_client()
        result = client.post(
            '/user',
            data={
                'first_name': 'jeena',
                'last_name': 'shah'
            },
            follow_redirects=False)
        result = client.get("/user")
        self.assertIn(b'jeena', result.data)

# get user edit form

    def test_usereditform(self):
        client = app.test_client()
        result = client.get("/user/edit/8")
        self.assertEqual(result.status_code, 200)

# edit user

    def test_useredit(self):
        client = app.test_client()
        result = client.patch(
            "/user/8",
            data={
                "first_name": "anjali",
                "last_name": "janii"
            },
            follow_redirects=True)
        self.assertIn(b'<h4>users list</h4>', result.data)

# get message form

    def test_messageform(self):
        client = app.test_client()
        result = client.get("user/8/message")
        self.assertIn(b'<h4>add message</h4>', result.data)


# edit message form

    def test_editmesage(self):
        client = app.test_client()
        result = client.patch(
            "/user/9/message/edit",
            data={"mtext": "hello vigi"},
            follow_redirects=True)
        self.assertIn(b'<h4>add message</h4>', result.data)

    # def test_userdelete(self):
    #     client = app.test_client()
    #     result = client.get("/user/delete/2")
    #     self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()