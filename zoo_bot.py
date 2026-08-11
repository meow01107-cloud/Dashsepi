import json
import random
import os

class ZooGame:
    def __init__(self):
        self.data_file = 'zoo_data.json'
        self.load_game()
    
    def load_game(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
            print('✅ بازی بارگذاری شد!')
        else:
            self.state = self.init_new_game()
            print('🎉 بازی جدید شروع شد!')
    
    def init_new_game(self):
        return {
            'money': 50000000,
            'day': 1,
            'weather': 'آفتابی',
            'animals': [
                {'id': 1, 'name': 'شیر', 'type': 'گوشت‌خوار', 'health': 100, 'happiness': 100, 'enclosure': 1},
                {'id': 2, 'name': 'فیل', 'type': 'علف‌خوار', 'health': 100, 'happiness': 100, 'enclosure': 2},
                {'id': 3, 'name': 'پنگوئن', 'type': 'پرنده', 'health': 100, 'happiness': 100, 'enclosure': 3},
                {'id': 4, 'name': 'مار', 'type': 'خزنده', 'health': 100, 'happiness': 100, 'enclosure': 4},
                {'id': 5, 'name': 'ببر', 'type': 'گوشت‌خوار', 'health': 100, 'happiness': 100, 'enclosure': 1},
                {'id': 6, 'name': 'زرافه', 'type': 'علف‌خوار', 'health': 100, 'happiness': 100, 'enclosure': 2},
                {'id': 7, 'name': 'تمساح', 'type': 'خزنده', 'health': 100, 'happiness': 100, 'enclosure': 4},
                {'id': 8, 'name': 'طوطی', 'type': 'پرنده', 'health': 100, 'happiness': 100, 'enclosure': 3}
            ],
            'enclosures': [
                {'id': 1, 'name': 'ساوانا', 'cleanliness': 100, 'capacity': 5},
                {'id': 2, 'name': 'جنگل', 'cleanliness': 100, 'capacity': 5},
                {'id': 3, 'name': 'یخچال', 'cleanliness': 100, 'capacity': 5},
                {'id': 4, 'name': 'باتلاق', 'cleanliness': 100, 'capacity': 5},
                {'id': 5, 'name': 'باغ', 'cleanliness': 100, 'capacity': 5}
            ],
            'staff': [
                {'id': 1, 'name': 'علی', 'role': 'نگهبان', 'salary': 2000000},
                {'id': 2, 'name': 'مریم', 'role': 'دامپزشک', 'salary': 3000000},
                {'id': 3, 'name': 'رضا', 'role': 'غذا‌ده', 'salary': 1500000},
                {'id': 4, 'name': 'سارا', 'role': 'راهنما', 'salary': 1800000}
            ],
            'visitors_today': 0,
            'total_visitors': 275,
            'logs': ['به باغ وحش هوشمند خوش آمدید!']
        }

    def save_game(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
        print('💾 بازی ذخیره شد.')

    def next_day(self):
        self.state['day'] += 1
        weathers = ['آفتابی', 'ابری', 'بارانی', 'برفی']
        self.state['weather'] = random.choice(weathers)
        
        for animal in self.state['animals']:
            animal['health'] = max(0, animal['health'] - random.randint(0, 5))
            animal['happiness'] = max(0, animal['happiness'] - random.randint(0, 10))
        
        for enc in self.state['enclosures']:
            enc['cleanliness'] = max(0, enc['cleanliness'] - random.randint(5, 15))
        
        visitors = random.randint(50, 200)
        income = visitors * 50000
        self.state['visitors_today'] = visitors
        self.state['total_visitors'] += visitors
        self.state['money'] += income
        
        total_salary = sum(s['salary'] for s in self.state['staff'])
        self.state['money'] -= total_salary
        
        self.state['logs'].append(f'روز {self.state["day"]}: {visitors} بازدیدکننده، درآمد: {income:,}')
        self.save_game()
        print(f'📅 روز {self.state["day"]} شروع شد. آب و هوا: {self.state["weather"]}')

    def monitor(self):
        print('\n=== 📊 مانیتورینگ باغ وحش ===')
        print(f'💰 پول: {self.state["money"]:,} تومان')
        print(f'📅 روز: {self.state["day"]} | 🌤️ آب و هوا: {self.state["weather"]}')
        print(f'👥 بازدیدکنندگان امروز: {self.state["visitors_today"]} | کل: {self.state["total_visitors"]}')
        
        alive = len([a for a in self.state['animals'] if a['health'] > 0])
        avg_health = sum(a['health'] for a in self.state['animals']) / len(self.state['animals'])
        print(f'🦁 حیوانات زنده: {alive} | میانگین سلامت: {avg_health:.1f}')
        
        avg_clean = sum(e['cleanliness'] for e in self.state['enclosures']) / len(self.state['enclosures'])
        print(f'🧹 میانگین تمیزی: {avg_clean:.1f}')
        print('============================\n')

    def run(self):
        while True:
            print('\n1. روز بعد 📅')
            print('2. مانیتورینگ 📊')
            print('3. ذخیره 💾')
            print('4. خروج 🚪')
            choice = input('انتخاب کنید: ')
            
            if choice == '1':
                self.next_day()
            elif choice == '2':
                self.monitor()
            elif choice == '3':
                self.save_game()
            elif choice == '4':
                print('خداحافظ! 👋')
                break

if __name__ == '__main__':
    game = ZooGame()
    game.run()
