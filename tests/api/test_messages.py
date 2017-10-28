import unittest
from unittest import mock

from groupy.api import messages


def get_fake_generic_message_data(**kwargs):
    data = {
        'id': 'foo',
        'created_at': 1302623328,
    }
    data.update(kwargs)
    return data


def get_fake_message_data(**kwargs):
    data = get_fake_generic_message_data()
    data['group_id'] = 'bar'
    data.update(kwargs)
    return data


def get_fake_direct_message_data(**kwargs):
    data = get_fake_generic_message_data()
    data['recipient_id'] = 'bar'
    data['sender_id'] = 'baz'
    data.update(kwargs)
    return data


def get_fake_response(code=200, data=None):
    response = mock.Mock()
    response.status_code = code
    response.data = data
    return response


class MessagesTests(unittest.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.messages = messages.Messages(self.m_session, group_id='bar')


class RawListMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        message = get_fake_message_data()
        response = get_fake_response(data={'messages': [message]})
        self.m_session.get.return_value = response
        self.results = self.messages._raw_list()

    def test_results_are_messages(self):
        self.assertTrue(all(isinstance(m, messages.Message) for m in self.results))


class EmptyRawListMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        message = get_fake_message_data()
        response = get_fake_response(code=304, data={'messages': [message]})
        self.m_session.get.return_value = response
        self.results = self.messages._raw_list()

    def test_results_are_empty(self):
        self.assertEqual(self.results, [])


class ListModesMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        self.messages.list = mock.Mock()

    def test_before(self):
        self.messages.list_before('qux')
        self.messages.list.called_once_with(before_id='qux')

    def test_after(self):
        self.messages.list_after('qux')
        self.messages.list.called_once_with(after_id='qux')

    def test_since(self):
        self.messages.list_since('qux')
        self.messages.list.called_once_with(since_id='qux')


class CreateTextMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        message = get_fake_message_data()
        response = get_fake_response(data={'message': message})
        self.m_session.post.return_value = response
        self.result = self.messages.create(text='qux')

    def test_result_is_message(self):
        self.assertTrue(isinstance(self.result, messages.Message))

    def test_payload_contains_text(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['message']
        self.assertEqual(message['text'], 'qux')

    def test_payload_lacks_attachments(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['message']
        self.assertNotIn('attachments', message)


class CreateAttachmentMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        message = get_fake_message_data()
        response = get_fake_response(data={'message': message})
        self.m_session.post.return_value = response
        m_attachment = mock.Mock()
        m_attachment.to_json.return_value = {'qux': 'quux'}
        self.result = self.messages.create(attachments=[m_attachment])

    def test_result_is_message(self):
        self.assertTrue(isinstance(self.result, messages.Message))

    def test_payload_contains_attachments(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['message']
        self.assertEqual(message['attachments'], [{'qux': 'quux'}])

    def test_payload_lacks_text(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['message']
        self.assertNotIn('text', message)


class DirectMessagesTests(unittest.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.messages = messages.DirectMessages(self.m_session,
                                                other_user_id='foo')


class RawListDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        message = get_fake_direct_message_data()
        response = get_fake_response(data={'direct_messages': [message]})
        self.m_session.get.return_value = response
        self.results = self.messages._raw_list()

    def test_results_are_direct_messages(self):
        self.assertTrue(all(isinstance(m, messages.DirectMessage) for m in self.results))


class EmptyRawListDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        message = get_fake_direct_message_data()
        response = get_fake_response(code=304, data={'direct_messages': [message]})
        self.m_session.get.return_value = response
        self.results = self.messages._raw_list()

    def test_results_are_empty(self):
        self.assertEqual(self.results, [])


class ListModesDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        self.messages.list = mock.Mock()

    def test_before(self):
        self.messages.list_before('qux')
        self.messages.list.called_once_with(before_id='qux')

    def test_since(self):
        self.messages.list_since('qux')
        self.messages.list.called_once_with(since_id='qux')


class CreateTextDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        message = get_fake_direct_message_data()
        response = get_fake_response(data={'direct_message': message})
        self.m_session.post.return_value = response
        self.result = self.messages.create(text='qux')

    def test_result_is_message(self):
        self.assertTrue(isinstance(self.result, messages.DirectMessage))

    def test_payload_contains_text(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs['json']
        self.assertEqual(payload['direct_message']['text'], 'qux')

    def test_payload_lacks_attachments(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['direct_message']
        self.assertNotIn('attachments', message)


class CreateAttachmentDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        message = get_fake_direct_message_data()
        response = get_fake_response(data={'direct_message': message})
        self.m_session.post.return_value = response
        m_attachment = mock.Mock()
        m_attachment.to_json.return_value = {'qux': 'quux'}
        self.result = self.messages.create(attachments=[m_attachment])

    def test_result_is_direct_message(self):
        self.assertTrue(isinstance(self.result, messages.DirectMessage))

    def test_payload_contains_attachments(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['direct_message']
        self.assertEqual(message['attachments'], [{'qux': 'quux'}])

    def test_payload_lacks_text(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['direct_message']
        self.assertNotIn('text', message)


class GenericMessageTests(unittest.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        data = get_fake_generic_message_data(name='Alice', text='corge')
        self.message = messages.GenericMessage(self.m_manager, 'qux', **data)


class LikeGenericMessageTests(GenericMessageTests):
    def setUp(self):
        super().setUp()
        self.message._likes = mock.Mock()

    def test_like_uses_likes(self):
        self.message.like()
        self.assertTrue(self.message._likes.like.called)

    def test_unlike_uses_likes(self):
        self.message.unlike()
        self.assertTrue(self.message._likes.unlike.called)


class GenericMessageReprTests(GenericMessageTests):
    def test_repr(self):
        representation = repr(self.message)
        self.assertEqual(representation, "<GenericMessage(name='Alice', "
                                         "text='corge', attachments=0)>")


class MessageTests(unittest.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        data = get_fake_message_data()
        self.message = messages.Message(self.m_manager, **data)

    def test_conversation_id_is_group_id(self):
        self.assertEqual(self.message.conversation_id, self.message.group_id)


class DirectMessageTests(unittest.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        data = get_fake_direct_message_data()
        self.message = messages.DirectMessage(self.m_manager, **data)

    def test_conversation_id_is_sender_and_recipient(self):
        self.assertEqual(self.message.conversation_id, 'bar+baz')


class AttachmentTests(unittest.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()


class AttachmentToJsonTests(AttachmentTests):
    def test_json_is_correct(self):
        a = messages.Attachment(self.m_manager, type='foo', text='bar')
        self.assertEqual(a.to_json(), {'type': 'foo', 'text': 'bar'})


class AttachmentsFromBulkDataTests(AttachmentTests):
    def setUp(self):
        super().setUp()
        self.data = [
            {'type': 'attachment', 'foo': 'bar'},
            {'type': 'location', 'baz': 'qux'},
        ]
        self.attachments = messages.Attachment.from_bulk_data(self.m_manager,
                                                              self.data)

    def test_attachment_one_is_attachment(self):
        self.assertEqual(type(self.attachments[0]), messages.Attachment)

    def test_attachment_two_is_location(self):
        self.assertIsInstance(self.attachments[1], messages.Location)


class LeaderboardTests(unittest.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.leaderboard = messages.Leaderboard(self.m_session, 'foo')


class GetMessagesLeaderboardTests(LeaderboardTests):
    def test_results_are_messages(self):
        message = get_fake_message_data()
        data = {'messages': [message]}
        self.m_session.get.return_value = get_fake_response(data=data)
        results = self.leaderboard._get_messages()
        self.assertTrue(all(isinstance(m, messages.Message) for m in results))