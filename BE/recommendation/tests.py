<<<<<<< HEAD
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from schedules.models import Schedules
from participants.models import Participants
from django.db.models import Count
import random

User = get_user_model()

class RecommendationTest(APITestCase):
    
    def setUp(self):
        # 추천을 받을 유저 생성
        self.user = User.objects.create_user(
            email = "recommendation@test.com",
            name = "LEE",
            nickname = "chan",
            gender = "0",
            password = "thisisneverthat"
        )
        self.client.force_authenticate(user=self.user)

    # 가상의 친구 5명 생성 
    def create_friends(self):
        
        self.friends = [
            User.objects.create_user(
                email = f"friend{i}@test.com",
                name = f"fnum{i}",
                nickname = f"ch{i}n",
                gender = '0',
                password = "thisisneverthat"
            )
            for i in range(1, 6) # 친구 5명 생성
        ]  

    # 3개월치 스케쥴 생성 (오늘보다 더 과거)
    def create_schedule(self):
        self.create_friends()

        for _ in range(50): # 스케줄 50개
            start_time = timezone.now() - timedelta(days=random.randint(1,90))
            end_time = start_time + timedelta(hours=3)

            schedules = Schedules.objects.create(
                created_by = self.user,
                schedule_start = start_time,
                schedule_end = end_time
            )
            
            # 스케쥴에 들어갈 친구들 (본인 포함)
            Participants.objects.create(schedule = schedules, participant = self.user)

            # 랜덤으로 1~5명의 친구 선택 (친구 수에 맞춰서)
            pick_random_friends = random.sample(self.friends, random.randint(1, len(self.friends)))
            for friend in pick_random_friends:
                Participants.objects.create(schedule = schedules, participant = friend)

    # 최근 3개월간 가장 많이 만난 친구와 그 평균 횟수
    def test_bestie_of_the_quarter(self):
        self.create_schedule()

        # 기준은 최근 3개월
        quarter_ago = timezone.now() - timedelta(days=90)
        
        # 유저의 최근 3개월 스케줄
        my_schedules = Schedules.objects.filter(
            schedule_start__gte= quarter_ago, # 최근 3개월
            participants__participant = self.user # 내가 참여한 스케쥴
        ).distinct() # 스케쥴 중복 제거

        friend_count = Participants.objects.filter(
            schedule__in = my_schedules
        ).exclude(
            participant = self.user # 나는 제외함
        ).values('participant__nickname').annotate(
            meet_count = Count('id')
        ).order_by('-meet_count')

        if friend_count.exists():
            best_friend = friend_count.first()
            print(f"가장 많이 만난 친구: {best_friend['participant__nickname']}")
            print(f"3개월간 만난 횟수: {best_friend['meet_count']}회")
            
            # 구체적인 검증
            self.assertIsNotNone(best_friend)
            self.assertGreater(best_friend['meet_count'], 0)
            self.assertIn('participant__nickname', best_friend)
            self.assertIn('meet_count', best_friend)
            
            # 모든 친구들의 만남 횟수가 0보다 큰지 확인
            for friend in friend_count:
                self.assertGreater(friend['meet_count'], 0)
                
            # 가장 많이 만난 친구가 정말 최대값인지 확인
            max_count = max(item['meet_count'] for item in friend_count)
            self.assertEqual(best_friend['meet_count'], max_count)
            
        else:
            print("3개월간 친구를 안만나셨네요..")
            self.fail("만난 친구가 없어서 테스트를 진행할 수 없습니다.")
=======
from django.test import TestCase

# Create your tests here.
>>>>>>> 740154d039bd1ec0cf34f5ea776bf555b914f9c9
