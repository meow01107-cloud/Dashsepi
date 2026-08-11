import json
import os
import random
from datetime import datetime

# تنظیمات اولیه بازی
DATA_FILE = "zoo_data.json"
ANIMAL_TYPES = ["شیر", "پلنگ", "فیل", "زرافه", "میمون", "خرس", "پاندا", "طوطی"]
ENCLOSURE_TYPES = ["ساوانا", "جنگل", "کوهستان", "آب‌بازی", "بیابان"]
STAFF_ROLES = ["نگهبان", "دامپزشک", "غذادهنده", "تمیزکار"]
WEATHER_CONDITIONS = ["آفتابی", "ابری", "بارانی", "برفی", "طوفانی"]

class ZooGame:
    def __init__(self):
        self.load_data()
        if not self.data:
            self.initialize_new_game()

    def initialize_new_game(self):
        """شروع بازی جدید با تنظیمات پیش‌فرض"""
        self.data = {
            "money": 50000000,
            "day": 1,
            "time": "08:00",
            "weather": "آفتابی",
            "animals": [],
            "enclosures": [
                {"id": i+1, "type": ENCLOSURE_TYPES[i % len(ENCLOSURE_TYPES)], "cleanliness": 100, "capacity": 5, "animals": []}
                for i in range(5)
            ],
            "staff": [
                {"id": i+1, "role": STAFF_ROLES[i % len(STAFF_ROLES)], "salary": 5000000, "efficiency": random.uniform(0.8, 1.0)}
                for i in range(4)
            ],
            "visitors_today": 0,
            "total_visitors": 0,
            "total_income": 0,
            "logs": ["بازی شروع شد! به باغ وحش خوش آمدید."]
        }
        self.add_animal("شیر", 0)
        self.add_animal("فیل", 1)
        self.add_animal("میمون", 2)
        self.save_data()

    def load_data(self):
        """بارگذاری داده‌ها از فایل"""
        self.data = None
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = None

    def save_data(self):
        """ذخیره داده‌ها در فایل"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_log(self, message):
        """ثبت رویداد در لاگ بازی"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.data["logs"].insert(0, f"[{timestamp}] {message}")
        if len(self.data["logs"]) > 50:
            self.data["logs"] = self.data["logs"][:50]
        self.save_data()

    def add_animal(self, animal_type, enclosure_id):
        """اضافه کردن حیوان به محوطه"""
        if enclosure_id >= len(self.data["enclosures"]):
            return False
        
        enclosure = self.data["enclosures"][enclosure_id]
        if len(enclosure["animals"]) >= enclosure["capacity"]:
            self.add_log(f"❌ محوطه {enclosure['type']} پر است!")
            return False
        
        cost = random.randint(1000000, 5000000)
        if self.data["money"] < cost:
            self.add_log(f"❌ پول کافی برای خرید {animal_type} ندارید!")
            return False
        
        new_animal = {
            "id": len(self.data["animals"]) + 1,
            "type": animal_type,
            "health": 100,
            "happiness": 100,
            "hunger": 0,
            "age": 0,
            "enclosure_id": enclosure_id,
            "alive": True
        }
        
        self.data["animals"].append(new_animal)
        enclosure["animals"].append(new_animal["id"])
        self.data["money"] -= cost
        self.add_log(f"✅ حیوان {animal_type} به محوطه {enclosure['type']} اضافه شد. ({cost:,} تومان)")
        self.save_data()
        return True

    def feed_animals(self):
        """غذا دادن به همه حیوانات"""
        food_cost = 500000
        if self.data["money"] < food_cost:
            self.add_log("❌ پول کافی برای خرید غذا ندارید!")
            return False
        
        fed_count = 0
        for animal in self.data["animals"]:
            if animal["alive"]:
                animal["hunger"] = max(0, animal["hunger"] - 30)
                animal["health"] = min(100, animal["health"] + 5)
                animal["happiness"] = min(100, animal["happiness"] + 10)
                fed_count += 1
        
        self.data["money"] -= food_cost
        self.add_log(f"✅ به {fed_count} حیوان غذا داده شد. ({food_cost:,} تومان)")
        self.save_data()
        return True

    def clean_enclosures(self):
        """تمیز کردن همه محوطه‌ها"""
        cleaning_cost = 300000
        if self.data["money"] < cleaning_cost:
            self.add_log("❌ پول کافی برای تمیزکاری ندارید!")
            return False
        
        for enclosure in self.data["enclosures"]:
            enclosure["cleanliness"] = 100
        
        self.data["money"] -= cleaning_cost
        self.add_log(f"✅ همه محوطه‌ها تمیز شدند. ({cleaning_cost:,} تومان)")
        self.save_data()
        return True

    def hire_staff(self, role):
        """استخدام کارمند جدید"""
        salary = 5000000
        if self.data["money"] < salary:
            self.add_log("❌ پول کافی برای استخدام ندارید!")
            return False
        
        new_staff = {
            "id": len(self.data["staff"]) + 1,
            "role": role,
            "salary": salary,
            "efficiency": random.uniform(0.7, 1.0)
        }
        
        self.data["staff"].append(new_staff)
        self.data["money"] -= salary
        self.add_log(f"✅ کارمند {role} استخدام شد. ({salary:,} تومان)")
        self.save_data()
        return True

    def process_day_end(self):
        """پردازش پایان روز"""
        self.data["day"] += 1
        self.data["time"] = "08:00"
        
        base_visitors = random.randint(50, 200)
        weather_effect = {"آفتابی": 1.2, "ابری": 1.0, "بارانی": 0.7, "برفی": 0.5, "طوفانی": 0.3}
        visitors = int(base_visitors * weather_effect.get(self.data["weather"], 1.0))
        
        alive_animals = [a for a in self.data["animals"] if a["alive"]]
        avg_happiness = sum(a["happiness"] for a in alive_animals) / max(1, len(alive_animals))
        avg_cleanliness = sum(e["cleanliness"] for e in self.data["enclosures"]) / len(self.data["enclosures"])
        
        visitor_factor = (avg_happiness / 100) * (avg_cleanliness / 100)
        final_visitors = int(visitors * visitor_factor)
        
        ticket_price = 50000
        daily_income = final_visitors * ticket_price
        
        self.data["visitors_today"] = final_visitors
        self.data["total_visitors"] += final_visitors
        self.data["total_income"] += daily_income
        self.data["money"] += daily_income
        
        for animal in self.data["animals"]:
            if animal["alive"]:
                animal["hunger"] += 20
                animal["age"] += 1
                
                if animal["hunger"] >= 100 or animal["health"] <= 0:
                    animal["alive"] = False
                    animal["health"] = 0
                    self.add_log(f"❌ حیوان {animal['type']} مرد!")
                
                if animal["hunger"] > 50:
                    animal["happiness"] -= 10
        
        for enclosure in self.data["enclosures"]:
            enclosure["cleanliness"] = max(0, enclosure["cleanliness"] - 15)
        
        if self.data["day"] % 7 == 0:
            total_salary = sum(s["salary"] for s in self.data["staff"])
            if self.data["money"] >= total_salary:
                self.data["money"] -= total_salary
                self.add_log(f"💰 حقوق کارمندان پرداخت شد. ({total_salary:,} تومان)")
            else:
                self.add_log("❌ پول کافی برای پرداخت حقوق کارمندان ندارید!")
                if self.data["staff"]:
                    fired = self.data["staff"].pop()
                    self.add_log(f"👋 کارمند {fired['role']} اخراج شد.")
        
        self.data["weather"] = random.choice(WEATHER_CONDITIONS)
        
        self.add_log(f"🌅 روز {self.data["day"]} شروع شد. آب و هوا: {self.data['weather']}")
        self.add_log(f"👥 بازدیدکنندگان امروز: {final_visitors} | درآمد: {daily_income:,} تومان")
        self.save_data()

    def get_monitoring_data(self):
        """دریافت داده‌های مانیتورینگ"""
        alive_animals = [a for a in self.data["animals"] if a["alive"]]
        total_animals = len(self.data["animals"])
        alive_count = len(alive_animals)
        
        avg_health = sum(a["health"] for a in alive_animals) / max(1, alive_count)
        avg_happiness = sum(a["happiness"] for a in alive_animals) / max(1, alive_count)
        avg_cleanliness = sum(e["cleanliness"] for e in self.data["enclosures"]) / len(self.data["enclosures"])
        
        return {
            "money": self.data["money"],
            "day": self.data["day"],
            "weather": self.data["weather"],
            "visitors_today": self.data["visitors_today"],
            "total_visitors": self.data["total_visitors"],
            "total_income": self.data["total_income"],
            "total_animals": total_animals,
            "alive_animals": alive_count,
            "avg_health": avg_health,
            "avg_happiness": avg_happiness,
            "avg_cleanliness": avg_cleanliness,
            "staff_count": len(self.data["staff"]),
            "logs": self.data["logs"][:10]
        }

    def show_menu(self):
        """نمایش منوی اصلی"""
        print("\n" + "="*50)
        print("🦁 باغ وحش هوشمند - منوی اصلی 🦁")
        print("="*50)
        print(f"💰 پول: {self.data['money']:,} تومان")
        print(f"📅 روز: {self.data['day']} | 🌤️ آب و هوا: {self.data['weather']}")
        print(f"👥 بازدیدکنندگان امروز: {self.data['visitors_today']}")
        print("="*50)
        print("1. 🦁 مدیریت حیوانات")
        print("2. 🏞️ مدیریت محوطه‌ها")
        print("3. 👷 مدیریت کارکنان")
        print("4. 🍖 غذا دادن به حیوانات")
        print("5. 🧹 تمیز کردن محوطه‌ها")
        print("6. 📊 گزارش وضعیت باغ وحش")
        print("7. 💰 گزارش مالی")
        print("8. 📜 مشاهده لاگ رویدادها")
        print("9. ⏭️ پایان روز")
        print("10. 📈 مانیتورینگ پیشرفته")
        print("0. ❌ خروج از بازی")
        print("="*50)

    def manage_animals(self):
        """مدیریت حیوانات"""
        while True:
            print("\n--- مدیریت حیوانات ---")
            print("1. ➕ اضافه کردن حیوان جدید")
            print("2. 📋 لیست حیوانات")
            print("0. 🔙 بازگشت")
            
            choice = input("انتخاب کنید: ")
            
            if choice == "1":
                print("\nانواع حیوانات:")
                for i, animal in enumerate(ANIMAL_TYPES):
                    print(f"{i+1}. {animal}")
                
                try:
                    animal_idx = int(input("شماره حیوان: ")) - 1
                    if 0 <= animal_idx < len(ANIMAL_TYPES):
                        print("\nمحوطه‌های موجود:")
                        for i, enc in enumerate(self.data["enclosures"]):
                            print(f"{i+1}. {enc['type']} (ظرفیت: {len(enc['animals'])}/{enc['capacity']})")
                        
                        enc_idx = int(input("شماره محوطه: ")) - 1
                        self.add_animal(ANIMAL_TYPES[animal_idx], enc_idx)
                    else:
                        print("❌ شماره نامعتبر!")
                except ValueError:
                    print("❌ ورودی نامعتبر!")
            
            elif choice == "2":
                print("\n--- لیست حیوانات ---")
                for animal in self.data["animals"]:
                    status = "✅ زنده" if animal["alive"] else "❌ مرده"
                    print(f"ID: {animal['id']} | نوع: {animal['type']} | سلامت: {animal['health']}% | شادی: {animal['happiness']}% | گرسنگی: {animal['hunger']}% | وضعیت: {status}")
            
            elif choice == "0":
                break

    def manage_enclosures(self):
        """مدیریت محوطه‌ها"""
        print("\n--- مدیریت محوطه‌ها ---")
        for enc in self.data["enclosures"]:
            print(f"محوطه {enc['id']}: {enc['type']} | تمیزی: {enc['cleanliness']}% | حیوانات: {len(enc['animals'])}/{enc['capacity']}")
        input("\nبرای بازگشت Enter بزنید...")

    def manage_staff(self):
        """مدیریت کارکنان"""
        while True:
            print("\n--- مدیریت کارکنان ---")
            print("1. ➕ استخدام کارمند جدید")
            print("2. 📋 لیست کارکنان")
            print("0. 🔙 بازگشت")
            
            choice = input("انتخاب کنید: ")
            
            if choice == "1":
                print("\nنقش‌های موجود:")
                for i, role in enumerate(STAFF_ROLES):
                    print(f"{i+1}. {role}")
                
                try:
                    role_idx = int(input("شماره نقش: ")) - 1
                    if 0 <= role_idx < len(STAFF_ROLES):
                        self.hire_staff(STAFF_ROLES[role_idx])
                    else:
                        print("❌ شماره نامعتبر!")
                except ValueError:
                    print("❌ ورودی نامعتبر!")
            
            elif choice == "2":
                print("\n--- لیست کارکنان ---")
                for staff in self.data["staff"]:
                    print(f"ID: {staff['id']} | نقش: {staff['role']} | حقوق: {staff['salary']:,} تومان | کارایی: {staff['efficiency']:.2f}")
            
            elif choice == "0":
                break

    def show_reports(self):
        """نمایش گزارش‌ها"""
        print("\n--- گزارش وضعیت باغ وحش ---")
        alive_animals = [a for a in self.data["animals"] if a["alive"]]
        print(f"کل حیوانات: {len(self.data['animals'])}")
        print(f"حیوانات زنده: {len(alive_animals)}")
        if alive_animals:
            print(f"میانگین سلامت: {sum(a['health'] for a in alive_animals)/len(alive_animals):.1f}%")
            print(f"میانگین شادی: {sum(a['happiness'] for a in alive_animals)/len(alive_animals):.1f}%")
        
        print(f"\nمیانگین تمیزی محوطه‌ها: {sum(e['cleanliness'] for e in self.data['enclosures'])/len(self.data['enclosures']):.1f}%")
        print(f"تعداد کارکنان: {len(self.data['staff'])}")
        print(f"کل بازدیدکنندگان: {self.data['total_visitors']}")
        input("\nبرای بازگشت Enter بزنید...")

    def show_financial_report(self):
        """نمایش گزارش مالی"""
        print("\n--- گزارش مالی ---")
        print(f"پول فعلی: {self.data['money']:,} تومان")
        print(f"کل درآمد: {self.data['total_income']:,} تومان")
        print(f"کل بازدیدکنندگان: {self.data['total_visitors']}")
        print(f"میانگین درآمد به ازای هر بازدیدکننده: {self.data['total_income']/max(1,self.data['total_visitors']):,.0f} تومان")
        input("\nبرای بازگشت Enter بزنید...")

    def show_logs(self):
        """نمایش لاگ رویدادها"""
        print("\n--- لاگ رویدادها ---")
        for log in self.data["logs"][:20]:
            print(log)
        input("\nبرای بازگشت Enter بزنید...")

    def advanced_monitoring(self):
        """مانیتورینگ پیشرفته با UI جذاب"""
        data = self.get_monitoring_data()
        
        print("\n" + "🔥"*30)
        print("📊 داشبورد مانیتورینگ پیشرفته باغ وحش 📊")
        print("🔥"*30)
        
        print(f"\n💰 وضعیت مالی:")
        print(f"   پول فعلی: {data['money']:,} تومان")
        print(f"   کل درآمد: {data['total_income']:,} تومان")
        
        print(f"\n📅 اطلاعات زمانی:")
        print(f"   روز بازی: {data['day']}")
        print(f"   آب و هوا: {data['weather']}")
        
        print(f"\n👥 آمار بازدیدکنندگان:")
        print(f"   امروز: {data['visitors_today']} نفر")
        print(f"   کل: {data['total_visitors']} نفر")
        
        print(f"\n🦁 وضعیت حیوانات:")
        print(f"   کل: {data['total_animals']} | زنده: {data['alive_animals']}")
        print(f"   میانگین سلامت: {data['avg_health']:.1f}% ❤️")
        print(f"   میانگین شادی: {data['avg_happiness']:.1f}% 😊")
        
        print(f"\n🧹 وضعیت محوطه‌ها:")
        print(f"   میانگین تمیزی: {data['avg_cleanliness']:.1f}% ✨")
        
        print(f"\n👷 نیروی انسانی:")
        print(f"   تعداد کارکنان: {data['staff_count']} نفر")
        
        print(f"\n📜 آخرین رویدادها:")
        for log in data['logs'][:5]:
            print(f"   {log}")
        
        print("\n" + "🔥"*30)
        input("برای بازگشت Enter بزنید...")

    def run(self):
        """اجرای اصلی بازی"""
        print("🦁 به باغ وحش هوشمند خوش آمدید! 🦁")
        
        while True:
            self.show_menu()
            choice = input("انتخاب کنید: ")
            
            if choice == "1":
                self.manage_animals()
            elif choice == "2":
                self.manage_enclosures()
            elif choice == "3":
                self.manage_staff()
            elif choice == "4":
                self.feed_animals()
            elif choice == "5":
                self.clean_enclosures()
            elif choice == "6":
                self.show_reports()
            elif choice == "7":
                self.show_financial_report()
            elif choice == "8":
                self.show_logs()
            elif choice == "9":
                confirm = input("آیا مطمئن هستید که می‌خواهید روز را پایان دهید؟ (y/n): ")
                if confirm.lower() == 'y':
                    self.process_day_end()
                    print("✅ روز با موفقیت پایان یافت!")
            elif choice == "10":
                self.advanced_monitoring()
            elif choice == "0":
                print("خداحافظ! 👋 امیدوارم دوباره ببینیمت!")
                break
            else:
                print("❌ انتخاب نامعتبر!")

if __name__ == "__main__":
    game = ZooGame()
    game.run()
