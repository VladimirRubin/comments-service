from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from backend.factories import PageCommentFactory


class APIBaseHistoryTestCase(TestCase):
    def test_get_history_for_comment(self):
        comment = PageCommentFactory(text='Initial Text')
        comment_id = comment.id

        comment.text = 'First Change'
        comment.save()

        comment.text = 'Second Change'
        comment.save()

        comment.text = 'Third Change'
        comment.save()

        comment.delete()

        res = self.client.get(reverse('historicalcomment-list'), {'id': comment_id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data['count'], 5)

        self.assertEqual(res.data['results'][0]['text'], 'Third Change')
        self.assertEqual(res.data['results'][0]['reason'], 'Deleted')

        self.assertEqual(res.data['results'][1]['text'], 'Third Change')
        self.assertEqual(res.data['results'][1]['reason'], 'Modified')

        self.assertEqual(res.data['results'][2]['text'], 'Second Change')
        self.assertEqual(res.data['results'][2]['reason'], 'Modified')

        self.assertEqual(res.data['results'][3]['text'], 'First Change')
        self.assertEqual(res.data['results'][3]['reason'], 'Modified')

        self.assertEqual(res.data['results'][4]['text'], 'Initial Text')
        self.assertEqual(res.data['results'][4]['reason'], 'Created')
