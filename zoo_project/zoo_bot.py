import json
import os
import time
import random
from datetime import datetime
from typing import Dict, List, Optional

# --- Configuration & Constants ---
DATA_FILE = "zoo_data.json"
LOG_FILE = "zoo_log.txt"

ANIMAL_TYPES = {
    "lion": {"name": "شیر", "cost": 5000000, "food_cost": 150000, "ticket_value": 25000, "hunger_rate": 15, "cleanliness_impact": -20},
    "elephant": {"name": "فیل", "cost": 8000000, "food_cost": 200000, "ticket_value": 30000, "hunger_rate": 10, "cleanliness_impact": -25},
    "zebra": {"name": "گورخر", "cost": 3000000, "food_cost": 80000, "ticket_value": 15000, "hunger_rate": 12, "cleanliness_impact": -10},
    "peacock": {"name": "طاووس", "cost": 1500000, "food_cost": 40000, "ticket_value": 10000, "hunger_rate": 5, "cleanliness_impact": -5}
}

ENCLOSURE_TYPES = {
    "savana": {"name": "ساوانا", "capacity": 5, "build_cost": 10000000, "animals": ["lion", "zebra"]},
    "jungle": {"name": "جنگل", "capacity": 4, "build_cost": 8000000, "animals": ["lion", "peacock"]},
    "waterland": {"name": "آب‌بازی", "capacity": 3, "build_cost": 12000000, "animals": ["elephant"]},
    "aviary": {"name": "پرنده‌خانه", "capacity": 10, "build_cost": 5000000, "animals": ["peacock"]},
    "general": {"name": "عمومی", "capacity": 6, "build_cost": 6000000, "animals": ["lion", "elephant", "zebra", "peacock"]}
}

STAFF_ROLES = {
    "keeper": {"name": "نگهبان", "salary": 300000, "efficiency": 1.0},
    "vet": {"name": "دامپزشک", "salary": 500000, "efficiency": 1.5},
    "cleaner": {"name": "رفتگر", "salary": 250000, "efficiency": 1.2},
    "guide": {"name": "راهنما", "salary": 200000, "efficiency": 1.1}
}

WEATHER_TYPES = ["آفتابی", "ابری", "بارانی", "طوفانی"]

class Animal:
    def __init__(self, animal_type: str, name: str, age: int = 1):
        self.type = animal_type
        self.name = name
        self.age = age
        self.hunger = 0  # 0 to 100
        self.health = 100  # 0 to 100
        self.happiness = 100  # 0 to 100
        self.is_alive = True
        self.last_fed = time.time()
        self.last_cleaned = time.time()

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "name": self.name,
            "age": self.age,
            "hunger": self.hunger,
            "health": self.health,
            "happiness": self.happiness,
            "is_alive": self.is_alive,
            "last_fed": self.last_fed,
            "last_cleaned": self.last_cleaned
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Animal':
        animal = cls(data["type"], data["name"], data["age"])
        animal.hunger = data["hunger"]
        animal.health = data["health"]
        animal.happiness = data["happiness"]
        animal.is_alive = data["is_alive"]
        animal.last_fed = data["last_fed"]
        animal.last_cleaned = data["last_cleaned"]
        return animal

class Enclosure:
    def __init__(self, enclosure_type: str, name: str):
        self.type = enclosure_type
        self.name = name
        self.animals: List[Animal] = []
        self.cleanliness = 100  # 0 to 100
        self.capacity = ENCLOSURE_TYPES[enclosure_type]["capacity"]

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "name": self.name,
            "animals": [a.to_dict() for a in self.animals],
            "cleanliness": self.cleanliness,
            "capacity": self.capacity
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Enclosure':
        enclosure = cls(data["type"], data["name"])
        enclosure.animals = [Animal.from_dict(a) for a in data["animals"]]
        enclosure.cleanliness = data["cleanliness"]
        enclosure.capacity = data["capacity"]
        return enclosure

class Staff:
    def __init__(self, role: str, name: str):
        self.role = role
        self.name = name
        self.salary = STAFF_ROLES[role]["salary"]
        self.efficiency = STAFF_ROLES[role]["efficiency"]

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "name": self.name,
            "salary": self.salary,
            "efficiency": self.efficiency
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Staff':
        staff = cls(data["role"], data["name"])
        staff.salary = data["salary"]
        staff.efficiency = data["efficiency"]
        return staff

class ZooGame:
    def __init__(self):
        self.money = 20000000  # Starting money
        self.day = 1
        self.weather = "آفتابی"
        self.enclosures: List[Enclosure] = []
        self.staff: List[Staff] = []
        self.visitors_today = 0
        self.total_visitors = 0
        self.logs: List[str] = []
        self.game_over = False
        
        self.load_game()
        if not self.enclosures and not self.staff:
            self.init_default_state()

    def init_default_state(self):
        self.log("بازی جدید شروع شد! به باغ وحش خود خوش آمدید.")
        # Create initial enclosures
        self.add_enclosure("savana", "محیط آفریقایی")
        self.add_enclosure("jungle", "جنگل انبوه")
        # Add initial animals
        self.add_animal(0, "lion", "شیرخان")
        self.add_animal(0, "zebra", "خط‌خطی")
        self.add_animal(1, "peacock", "زیباپر")
        # Hire initial staff
        self.hire_staff("keeper", "علی نگهبان")
        self.hire_staff("cleaner", "رضا رفتگر")

    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def save_game(self):
        data = {
            "money": self.money,
            "day": self.day,
            "weather": self.weather,
            "enclosures": [e.to_dict() for e in self.enclosures],
            "staff": [s.to_dict() for s in self.staff],
            "visitors_today": self.visitors_today,
            "total_visitors": self.total_visitors,
            "logs": self.logs[-50:]  # Keep last 50 logs
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"بازی ذخیره شد در {DATA_FILE}")

    def load_game(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.money = data["money"]
                self.day = data["day"]
                self.weather = data["weather"]
                self.enclosures = [Enclosure.from_dict(e) for e in data["enclosures"]]
                self.staff = [Staff.from_dict(s) for s in data["staff"]]
                self.visitors_today = data["visitors_today"]
                self.total_visitors = data["total_visitors"]
                self.logs = data.get("logs", [])
                print("بازی قبلی بارگذاری شد.")
                return True
            except Exception as e:
                print(f"خطا در بارگذاری بازی: {e}")
                return False
        return False

    def add_enclosure(self, enclosure_type: str, name: str) -> bool:
        if enclosure_type not in ENCLOSURE_TYPES:
            self.log("نوع محیط نامعتبر است.")
            return False
        
        cost = ENCLOSURE_TYPES[enclosure_type]["build_cost"]
        if self.money < cost:
            self.log(f"پول کافی برای ساخت {name} ندارید. هزینه: {cost:,} تومان")
            return False
        
        self.money -= cost
        self.enclosures.append(Enclosure(enclosure_type, name))
        self.log(f"محیط {name} ({ENCLOSURE_TYPES[enclosure_type]['name']}) ساخته شد.")
        return True

    def add_animal(self, enclosure_index: int, animal_type: str, name: str) -> bool:
        if enclosure_index < 0 or enclosure_index >= len(self.enclosures):
            self.log("شماره محیط نامعتبر است.")
            return False
        
        enclosure = self.enclosures[enclosure_index]
        if animal_type not in ENCLOSURE_TYPES[enclosure.type]["animals"]:
            self.log(f"حیوان {ANIMAL_TYPES[animal_type]['name']} نمی‌تواند در {ENCLOSURE_TYPES[enclosure.type]['name']} زندگی کند.")
            return False
        
        if len(enclosure.animals) >= enclosure.capacity:
            self.log(f"ظرفیت {enclosure.name} پر است.")
            return False
        
        cost = ANIMAL_TYPES[animal_type]["cost"]
        if self.money < cost:
            self.log(f"پول کافی برای خرید {ANIMAL_TYPES[animal_type]['name']} ندارید. هزینه: {cost:,} تومان")
            return False
        
        self.money -= cost
        animal = Animal(animal_type, name)
        enclosure.animals.append(animal)
        self.log(f"حیوان {name} ({ANIMAL_TYPES[animal_type]['name']}) به {enclosure.name} اضافه شد.")
        return True

    def hire_staff(self, role: str, name: str) -> bool:
        if role not in STAFF_ROLES:
            self.log("نقش کارمند نامعتبر است.")
            return False
        
        salary = STAFF_ROLES[role]["salary"]
        # Check if we can afford first month salary
        if self.money < salary:
            self.log(f"پول کافی برای استخدام {name} ندارید. حقوق ماهانه: {salary:,} تومان")
            return False
        
        self.staff.append(Staff(role, name))
        self.log(f"کارمند {name} ({STAFF_ROLES[role]['name']}) استخدام شد.")
        return True

    def feed_animal(self, enclosure_index: int, animal_index: int) -> bool:
        if enclosure_index < 0 or enclosure_index >= len(self.enclosures):
            return False
        enclosure = self.enclosures[enclosure_index]
        if animal_index < 0 or animal_index >= len(enclosure.animals):
            return False
        
        animal = enclosure.animals[animal_index]
        if not animal.is_alive:
            self.log(f"{animal.name} مرده است و نمی‌تواند غذا بخورد.")
            return False
        
        food_cost = ANIMAL_TYPES[animal.type]["food_cost"]
        if self.money < food_cost:
            self.log("پول کافی برای خرید غذا ندارید.")
            return False
        
        self.money -= food_cost
        animal.hunger = max(0, animal.hunger - 50)
        animal.happiness = min(100, animal.happiness + 10)
        animal.last_fed = time.time()
        self.log(f"{animal.name} غذا خورد. گرسنگی: {animal.hunger}%")
        return True

    def clean_enclosure(self, enclosure_index: int) -> bool:
        if enclosure_index < 0 or enclosure_index >= len(self.enclosures):
            return False
        
        enclosure = self.enclosures[enclosure_index]
        # Find cleaners
        cleaners = [s for s in self.staff if s.role == "cleaner"]
        if not cleaners:
            self.log("هیچ رفتگری برای تمیز کردن وجود ندارد.")
            return False
        
        efficiency = sum(c.efficiency for c in cleaners)
        cleanliness_boost = min(100, 30 * efficiency)
        enclosure.cleanliness = min(100, enclosure.cleanliness + cleanliness_boost)
        
        # Pay cleaners per task (small amount)
        task_payment = 5000
        total_payment = task_payment * len(cleaners)
        if self.money >= total_payment:
            self.money -= total_payment
            self.log(f"{enclosure.name} تمیز شد. تمیزی: {enclosure.cleanliness}%")
            return True
        else:
            self.log("پول کافی برای پرداخت به رفتگرها ندارید.")
            return False

    def treat_animal(self, enclosure_index: int, animal_index: int) -> bool:
        if enclosure_index < 0 or enclosure_index >= len(self.enclosures):
            return False
        enclosure = self.enclosures[enclosure_index]
        if animal_index < 0 or animal_index >= len(enclosure.animals):
            return False
        
        animal = enclosure.animals[animal_index]
        if not animal.is_alive:
            return False
        
        vets = [s for s in self.staff if s.role == "vet"]
        if not vets:
            self.log("هیچ دامپزشکی برای درمان وجود ندارد.")
            return False
        
        treatment_cost = 100000
        if self.money < treatment_cost:
            self.log("پول کافی برای درمان ندارید.")
            return False
        
        self.money -= treatment_cost
        efficiency = sum(v.efficiency for v in vets)
        health_boost = min(100, 40 * efficiency)
        animal.health = min(100, animal.health + health_boost)
        animal.happiness = min(100, animal.happiness + 15)
        self.log(f"{animal.name} درمان شد. سلامت: {animal.health}%")
        return True

    def process_day(self):
        self.log(f"--- روز {self.day} شروع شد ---")
        self.weather = random.choice(WEATHER_TYPES)
        self.log(f"آب و هوا: {self.weather}")
        
        # Weather effects
        weather_multiplier = 1.0
        if self.weather == "بارانی":
            weather_multiplier = 0.7
        elif self.weather == "طوفانی":
            weather_multiplier = 0.4
        
        # Process each enclosure
        for enclosure in self.enclosures:
            # Decrease cleanliness over time
            enclosure.cleanliness = max(0, enclosure.cleanliness - 5)
            
            # Process each animal
            dead_animals = []
            for i, animal in enumerate(enclosure.animals):
                if not animal.is_alive:
                    continue
                
                # Increase hunger
                hunger_increase = ANIMAL_TYPES[animal.type]["hunger_rate"]
                if self.weather == "سرد":
                    hunger_increase *= 1.2
                animal.hunger = min(100, animal.hunger + hunger_increase)
                
                # Health effects
                if animal.hunger > 80:
                    animal.health -= 10
                    animal.happiness -= 5
                if enclosure.cleanliness < 30:
                    animal.health -= 5
                    animal.happiness -= 10
                
                # Happiness decay
                animal.happiness = max(0, animal.happiness - 2)
                
                # Check death
                if animal.health <= 0:
                    animal.is_alive = False
                    dead_animals.append(i)
                    self.log(f"متاسفانه {animal.name} مرد!")
                
                # Age animals occasionally
                if random.random() < 0.01:  # 1% chance per day to age
                    animal.age += 1
            
            # Remove dead animals
            for i in sorted(dead_animals, reverse=True):
                enclosure.animals.pop(i)
        
        # Calculate visitors and income
        base_visitors = sum(len(e.animals) for e in self.enclosures) * 50
        if not self.enclosures or all(len(e.animals) == 0 for e in self.enclosures):
            base_visitors = 0
        
        # Staff effect on visitors
        guides = [s for s in self.staff if s.role == "guide"]
        guide_bonus = sum(g.efficiency * 10 for g in guides)
        
        # Cleanliness effect
        avg_cleanliness = sum(e.cleanliness for e in self.enclosures) / max(1, len(self.enclosures))
        cleanliness_factor = avg_cleanliness / 100.0
        
        visitors = int(base_visitors * weather_multiplier * cleanliness_factor + guide_bonus)
        visitors = max(0, visitors)
        
        ticket_price = 50000  # Base ticket price
        # Animal variety bonus
        unique_animals = set()
        for e in self.enclosures:
            for a in e.animals:
                if a.is_alive:
                    unique_animals.add(a.type)
        
        if len(unique_animals) > 2:
            ticket_price *= 1.1
        if len(unique_animals) > 3:
            ticket_price *= 1.1
            
        daily_income = visitors * ticket_price
        self.visitors_today = visitors
        self.total_visitors += visitors
        self.money += daily_income
        
        self.log(f"بازدیدکنندگان امروز: {visitors} نفر")
        self.log(f"درآمد بلیط: {daily_income:,} تومان")
        
        # Pay staff salaries (daily portion)
        daily_salary_total = 0
        for s in self.staff:
            daily_salary = s.salary // 30  # Approximate daily salary
            daily_salary_total += daily_salary
        
        if self.money >= daily_salary_total:
            self.money -= daily_salary_total
            self.log(f"حقوق کارکنان پرداخت شد: {daily_salary_total:,} تومان")
        else:
            self.log("هشدار: پول کافی برای پرداخت حقوق کارکنان ندارید!")
            # Fire staff if can't pay? No, let player decide
        
        self.day += 1
        self.save_game()
        self.log(f"--- روز {self.day-1} پایان یافت ---")
        
        # Check game over conditions
        if self.money < -5000000:  # Bankruptcy
            self.log("ورشکست شدید! بازی تمام شد.")
            self.game_over = True
        elif not any(e.animals for e in self.enclosures) and self.day > 10:
            self.log("همه حیوانات مردند و باغ وحش تعطیل شد!")
            self.game_over = True

    def get_status(self) -> str:
        status = f"""
=== وضعیت باغ وحش ===
روز: {self.day} | آب و هوا: {self.weather}
پول: {self.money:,} تومان
بازدیدکنندگان کل: {self.total_visitors:,} نفر
تعداد محیط‌ها: {len(self.enclosures)}
تعداد کارکنان: {len(self.staff)}

"""
        for i, enclosure in enumerate(self.enclosures):
            status += f"\n[{i}] {enclosure.name} ({ENCLOSURE_TYPES[enclosure.type]['name']}) - تمیزی: {enclosure.cleanliness}%"
            status += f"\n    حیوانات ({len(enclosure.animals)}/{enclosure.capacity}):"
            for j, animal in enumerate(enclosure.animals):
                if animal.is_alive:
                    status += f"\n      [{j}] {animal.name} ({ANIMAL_TYPES[animal.type]['name']}) - گرسنگی: {animal.hunger}%، سلامت: {animal.health}%، شادی: {animal.happiness}%"
                else:
                    status += f"\n      [{j}] {animal.name} (مرده)"
        
        status += "\n\nکارکنان:"
        for i, s in enumerate(self.staff):
            status += f"\n  [{i}] {s.name} ({STAFF_ROLES[s.role]['name']}) - حقوق: {s.salary:,}"
        
        return status

    def get_monitoring_data(self) -> dict:
        """Returns structured data for monitoring UI"""
        total_animals = sum(len(e.animals) for e in self.enclosures)
        alive_animals = sum(sum(1 for a in e.animals if a.is_alive) for e in self.enclosures)
        avg_health = 0
        avg_happiness = 0
        if alive_animals > 0:
            total_health = sum(a.health for e in self.enclosures for a in e.animals if a.is_alive)
            total_happiness = sum(a.happiness for e in self.enclosures for a in e.animals if a.is_alive)
            avg_health = total_health / alive_animals
            avg_happiness = total_happiness / alive_animals
        
        avg_cleanliness = sum(e.cleanliness for e in self.enclosures) / max(1, len(self.enclosures))
        
        return {
            "day": self.day,
            "weather": self.weather,
            "money": self.money,
            "total_visitors": self.total_visitors,
            "visitors_today": self.visitors_today,
            "enclosures_count": len(self.enclosures),
            "staff_count": len(self.staff),
            "total_animals": total_animals,
            "alive_animals": alive_animals,
            "avg_health": round(avg_health, 1),
            "avg_happiness": round(avg_happiness, 1),
            "avg_cleanliness": round(avg_cleanliness, 1),
            "logs": self.logs[-10:]  # Last 10 logs
        }

def main():
    game = ZooGame()
    
    while not game.game_over:
        print("\n" + "="*50)
        print("منوی اصلی باغ وحش")
        print("="*50)
        print("1. مشاهده وضعیت")
        print("2. گذراندن روز")
        print("3. افزودن محیط")
        print("4. افزودن حیوان")
        print("5. استخدام کارمند")
        print("6. غذا دادن به حیوان")
        print("7. تمیز کردن محیط")
        print("8. درمان حیوان")
        print("9. ذخیره و خروج")
        print("10. مانیتورینگ پیشرفته")
        
        choice = input("\nانتخاب شما (1-10): ").strip()
        
        if choice == "1":
            print(game.get_status())
        elif choice == "2":
            game.process_day()
        elif choice == "3":
            print("\nانواع محیط:")
            for key, val in ENCLOSURE_TYPES.items():
                print(f"  {key}: {val['name']} (ظرفیت: {val['capacity']}, هزینه: {val['build_cost']:,})")
            try:
                enc_type = input("نوع محیط: ").strip()
                enc_name = input("نام محیط: ").strip()
                game.add_enclosure(enc_type, enc_name)
            except Exception as e:
                print(f"خطا: {e}")
        elif choice == "4":
            print(game.get_status())
            try:
                enc_idx = int(input("شماره محیط: ").strip())
                print("\nانواع حیوان:")
                for key, val in ANIMAL_TYPES.items():
                    print(f"  {key}: {val['name']} (هزینه: {val['cost']:,})")
                anim_type = input("نوع حیوان: ").strip()
                anim_name = input("نام حیوان: ").strip()
                game.add_animal(enc_idx, anim_type, anim_name)
            except Exception as e:
                print(f"خطا: {e}")
        elif choice == "5":
            print("\nنقش‌های کارمندی:")
            for key, val in STAFF_ROLES.items():
                print(f"  {key}: {val['name']} (حقوق: {val['salary']:,})")
            try:
                role = input("نقش: ").strip()
                name = input("نام: ").strip()
                game.hire_staff(role, name)
            except Exception as e:
                print(f"خطا: {e}")
        elif choice == "6":
            print(game.get_status())
            try:
                enc_idx = int(input("شماره محیط: ").strip())
                anim_idx = int(input("شماره حیوان: ").strip())
                game.feed_animal(enc_idx, anim_idx)
            except Exception as e:
                print(f"خطا: {e}")
        elif choice == "7":
            print(game.get_status())
            try:
                enc_idx = int(input("شماره محیط: ").strip())
                game.clean_enclosure(enc_idx)
            except Exception as e:
                print(f"خطا: {e}")
        elif choice == "8":
            print(game.get_status())
            try:
                enc_idx = int(input("شماره محیط: ").strip())
                anim_idx = int(input("شماره حیوان: ").strip())
                game.treat_animal(enc_idx, anim_idx)
            except Exception as e:
                print(f"خطا: {e}")
        elif choice == "9":
            game.save_game()
            print("خداحافظ!")
            break
        elif choice == "10":
            data = game.get_monitoring_data()
            print("\n" + "="*50)
            print("📊 داشبورد مانیتورینگ پیشرفته")
            print("="*50)
            print(f"📅 روز: {data['day']} | 🌤️ آب و هوا: {data['weather']}")
            print(f"💰 پول: {data['money']:,} تومان")
            print(f"👥 بازدیدکنندگان امروز: {data['visitors_today']} | کل: {data['total_visitors']:,}")
            print(f"🏠 محیط‌ها: {data['enclosures_count']} | 👷 کارکنان: {data['staff_count']}")
            print(f"🦁 حیوانات زنده: {data['alive_animals']}/{data['total_animals']}")
            print(f"❤️ میانگین سلامت: {data['avg_health']}% | 😊 شادی: {data['avg_happiness']}% | 🧹 تمیزی: {data['avg_cleanliness']}%")
            print("\n📝 آخرین رویدادها:")
            for log in data['logs']:
                print(f"  {log}")
            input("\nبرای بازگشت Enter بزنید...")
        else:
            print("انتخاب نامعتبر!")

if __name__ == "__main__":
    main()
