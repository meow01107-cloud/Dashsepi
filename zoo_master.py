#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
پروژه جامع مدیریت باغ وحش هوشمند (Zoo Master Simulator)
نویسنده: دستیار هوشمند
توضیحات: شبیه‌سازی کامل اکوسیستم باغ وحش شامل حیوانات، پرسنل، بازدیدکنندگان، اقتصاد و رویدادهای پویا.
"""

import random
import json
import time
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any

# ==========================================
# تنظیمات و ثابت‌ها (Constants & Config)
# ==========================================

class Config:
    START_MONEY = 50000000  # سرمایه اولیه (تومان)
    TICKET_PRICE = 50000    # قیمت بلیط ورودی
    MAX_ZOO_CAPACITY = 500  # ظرفیت کل باغ وحش
    DAY_DURATION_SECONDS = 5  # هر روز شبیه‌سازی چند ثانیه واقعی طول می‌کشد (برای نمایش)
    
    # ضرایب اثرگذاری
    HUNGER_DECREASE_RATE = 5
    ENERGY_DECREASE_RATE = 2
    HAPPINESS_DECREASE_RATE = 3
    DIRT_INCREASE_RATE = 2

# ==========================================
# شمارنده‌ها و انواع (Enums)
# ==========================================

class AnimalType(Enum):
    MAMMAL = "پستاندار"
    BIRD = "پرنده"
    REPTILE = "خزنده"
    AMPHIBIAN = "دوزیست"

class DietType(Enum):
    CARNIVORE = "گوشت‌خوار"
    HERBIVORE = "گیاه‌خوار"
    OMNIVORE = "همه‌چیزخوار"

class WeatherCondition(Enum):
    SUNNY = "آفتابی"
    CLOUDY = "ابری"
    RAINY = "بارانی"
    STORMY = "طوفانی"

class StaffRole(Enum):
    KEEPER = "نگهبان/شیرده"
    VET = "دامپزشک"
    GUIDE = "راهنما"
    CLEANER = "نظافتچی"

class HealthStatus(Enum):
    HEALTHY = "سالم"
    SICK = "بیمار"
    INJURED = "مجروح"
    CRITICAL = "بحرانی"

# ==========================================
# کلاس‌های پایه و کمکی (Base & Utility Classes)
# ==========================================

class Logger:
    """سیستم ثبت وقایع باغ وحش"""
    def __init__(self):
        self.logs: List[str] = []

    def add_log(self, message: str, category: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{category}] {message}"
        self.logs.append(log_entry)
        # در نسخه واقعی اینجا در فایل ذخیره می‌شود
        print(log_entry)

    def get_report(self) -> str:
        return "\n".join(self.logs[-50:])  # 50 لاگ آخر

logger = Logger()

class Coordinate:
    """نمایش مختصات در نقشه باغ وحش"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def distance_to(self, other: 'Coordinate') -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5

    def __str__(self):
        return f"({self.x}, {self.y})"

# ==========================================
# کلاس‌های مرتبط با حیوانات (Animal System)
# ==========================================

class Animal(ABC):
    def __init__(self, name: str, age: int, gender: str, diet: DietType, animal_type: AnimalType):
        self.id = random.randint(1000, 9999)
        self.name = name
        self.age = age
        self.gender = gender
        self.diet = diet
        self.animal_type = animal_type
        
        # وضعیت فیزیولوژیک
        self.hunger = 100  # 100 = سیر، 0 = گرسنه مطلق
        self.energy = 100  # 100 = پرانرژی، 0 = خسته مطلق
        self.happiness = 100 # 100 = خوشحال، 0 = افسرده
        self.health_status = HealthStatus.HEALTHY
        self.hygiene = 100 # میزان تمیزی
        
        self.location: Optional[Coordinate] = None
        self.enclosure_id: Optional[int] = None
        self.is_sleeping = False
        self.price = self._calculate_price()

    def _calculate_price(self) -> int:
        base_price = 5000000
        if self.diet == DietType.CARNIVORE: base_price *= 1.5
        if self.animal_type == AnimalType.REPTILE: base_price *= 0.8
        return int(base_price + (self.age * 100000))

    @abstractmethod
    def make_sound(self) -> str:
        pass

    @abstractmethod
    def special_action(self) -> str:
        pass

    def tick(self, weather: WeatherCondition, is_night: bool):
        """بروزرسانی وضعیت حیوان در هر تیک زمانی"""
        if self.health_status == HealthStatus.CRITICAL:
            logger.add_log(f"{self.name} در وضعیت بحرانی است!", "WARNING")
            return

        # تأثیر شب و روز
        if is_night:
            self.is_sleeping = True
            self.energy = min(100, self.energy + 10)
            self.hunger -= (Config.HUNGER_DECREASE_RATE * 0.5) # شب‌ها کمتر گرسنه می‌شوند
        else:
            self.is_sleeping = False
            self.energy -= Config.ENERGY_DECREASE_RATE
            self.hunger -= Config.HUNGER_DECREASE_RATE
            
            # تأثیر آب و هوا
            if weather == WeatherCondition.STORMY:
                self.happiness -= 10
                self.energy -= 5
            elif weather == WeatherCondition.SUNNY:
                self.happiness += 2

        # کاهش شادی به مرور زمان
        self.happiness -= Config.HAPPINESS_DECREASE_RATE
        
        # محدود کردن مقادیر بین 0 و 100
        self.hunger = max(0, min(100, self.hunger))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))

        # بررسی بیماری
        if self.hunger < 20 or self.happiness < 20 or self.hygiene < 30:
            if random.random() < 0.1: # 10% شانس بیمار شدن
                self.health_status = HealthStatus.SICK
                logger.add_log(f"{self.name} بیمار شد!", "ALERT")

    def feed(self, food_amount: int):
        if self.is_sleeping:
            return "خواب است و غذا نمی‌خورد."
        self.hunger = min(100, self.hunger + food_amount)
        self.happiness += 5
        return f"{self.name} غذا خورد و سیر شد."

    def clean(self):
        self.hygiene = 100
        self.happiness += 10
        return f"{self.name} تمیز شد."

    def treat(self):
        if self.health_status != HealthStatus.HEALTHY:
            self.health_status = HealthStatus.HEALTHY
            self.happiness += 20
            return f"{self.name} درمان شد."
        return f"{self.name} سالم است."

    def get_status_str(self) -> str:
        status_icon = "🟢" if self.health_status == HealthStatus.HEALTHY else "🔴"
        sleep_icon = "💤" if self.is_sleeping else "👁️"
        return (f"{status_icon} {sleep_icon} {self.name} ({self.diet.value}): "
                f"گرسنگی:{int(self.hunger)} | انرژی:{int(self.energy)} | شادی:{int(self.happiness)} | بهداشت:{int(self.hygiene)}")

class Lion(Animal):
    def __init__(self, name: str, age: int, gender: str):
        super().__init__(name, age, gender, DietType.CARNIVORE, AnimalType.MAMMAL)
        self.price = 15000000

    def make_sound(self): return "غرررررش!"
    def special_action(self): return "در حال تیز کردن چنگال‌ها..."

class Elephant(Animal):
    def __init__(self, name: str, age: int, gender: str):
        super().__init__(name, age, gender, DietType.HERBIVORE, AnimalType.MAMMAL)
        self.price = 20000000

    def make_sound(self): return "فیییییل!"
    def special_action(self): return "با خرطوم آب بازی می‌کند."

class Penguin(Animal):
    def __init__(self, name: str, age: int, gender: str):
        super().__init__(name, age, gender, DietType.OMNIVORE, AnimalType.BIRD)
        self.price = 8000000

    def make_sound(self): return "هو هو!"
    def special_action(self): return "در حال سر خوردن روی یخ."

class Snake(Animal):
    def __init__(self, name: str, age: int, gender: str):
        super().__init__(name, age, gender, DietType.CARNIVORE, AnimalType.REPTILE)
        self.price = 4000000

    def make_sound(self): return "فیسسسس..."
    def special_action(self): return "در حال پوست اندازی."

# ==========================================
# کلاس‌های محیط و محوطه (Enclosure System)
# ==========================================

class Enclosure:
    def __init__(self, id: int, name: str, capacity: int, theme: str):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.theme = theme  # مثلا: جنگلی، بیابانی، قطبی
        self.animals: List[Animal] = []
        self.cleanliness = 100 # 0 تا 100
        self.facility_health = 100 # سلامت قفس و تجهیزات

    def add_animal(self, animal: Animal):
        if len(self.animals) >= self.capacity:
            raise ValueError(f"محوطه {self.name} پر است!")
        animal.enclosure_id = self.id
        # فرض می‌کنیم مختصات وسط محوطه است (ساده‌سازی شده)
        animal.location = Coordinate(self.id * 10, 50) 
        self.animals.append(animal)
        logger.add_log(f"{animal.name} به محوطه {self.name} اضافه شد.")

    def remove_animal(self, animal_id: int):
        for animal in self.animals:
            if animal.id == animal_id:
                self.animals.remove(animal)
                logger.add_log(f"{animal.name} از محوطه {self.name} حذف شد.")
                return True
        return False

    def tick(self):
        # کثیف شدن محوطه بر اساس تعداد حیوانات
        dirt_rate = len(self.animals) * Config.DIRT_INCREASE_RATE
        self.cleanliness = max(0, self.cleanliness - dirt_rate)
        
        if self.cleanliness < 30:
            for animal in self.animals:
                animal.hygiene -= 5
                if random.random() < 0.05:
                    animal.health_status = HealthStatus.SICK

    def clean_enclosure(self):
        self.cleanliness = 100
        for animal in self.animals:
            animal.clean()
        logger.add_log(f"محوطه {self.name} کاملاً تمیز شد.")

    def get_status(self) -> str:
        animal_names = ", ".join([a.name for a in self.animals]) or "خالی"
        return (f"محوطه [{self.name}] ({self.theme}): "
                f"ظرفیت: {len(self.animals)}/{self.capacity} | "
                f"تمیزی: {self.cleanliness}% | "
                f"ساکنین: {animal_names}")

# ==========================================
# کلاس‌های پرسنل (Staff System)
# ==========================================

class StaffMember:
    def __init__(self, name: str, role: StaffRole, salary: int):
        self.name = name
        self.role = role
        self.salary = salary
        self.energy = 100
        self.skill_level = random.randint(1, 10) # سطح مهارت 1 تا 10

    def work(self, zoo: 'Zoo'):
        if self.energy < 10:
            return f"{self.name} خیلی خسته است و نیاز به استراحت دارد."
        
        action_result = ""
        self.energy -= 20

        if self.role == StaffRole.KEEPER:
            # تغذیه حیوانات گرسنه
            fed_count = 0
            for enc in zoo.enclosures:
                for animal in enc.animals:
                    if animal.hunger < 50 and not animal.is_sleeping:
                        animal.feed(40)
                        fed_count += 1
            action_result = f"{self.name} به {fed_count} حیوان غذا داد."

        elif self.role == StaffRole.VET:
            # درمان حیوانات بیمار
            treated_count = 0
            for enc in zoo.enclosures:
                for animal in enc.animals:
                    if animal.health_status != HealthStatus.HEALTHY:
                        animal.treat()
                        treated_count += 1
            action_result = f"{self.name} {treated_count} حیوان را معالجه کرد."

        elif self.role == StaffRole.CLEANER:
            # تمیز کردن محوطه‌های کثیف
            cleaned_count = 0
            for enc in zoo.enclosures:
                if enc.cleanliness < 70:
                    enc.clean_enclosure()
                    cleaned_count += 1
            action_result = f"{self.name} {cleaned_count} محوطه را تمیز کرد."

        elif self.role == StaffRole.GUIDE:
            # افزایش شادی بازدیدکنندگان (تأثیر غیرمستقیم)
            zoo.visitor_satisfaction_boost += 10 * self.skill_level
            action_result = f"{self.name} تور گردشگری برگزار کرد و رضایت را افزایش داد."

        logger.add_log(action_result, "STAFF")
        return action_result

    def rest(self):
        self.energy = min(100, self.energy + 50)
        return f"{self.name} استراحت کرد."

# ==========================================
# سیستم بازدیدکنندگان و اقتصاد (Visitor & Economy)
# ==========================================

class VisitorManager:
    def __init__(self):
        self.current_visitors = 0
        self.total_visitors_today = 0
        self.satisfaction_avg = 100 # میانگین رضایت
        self.revenue_today = 0

    def simulate_arrival(self, weather: WeatherCondition, zoo_quality: int, is_weekend: bool):
        # فرمول جذب بازدیدکننده
        base_flow = 100 if is_weekend else 50
        
        weather_factor = 1.0
        if weather == WeatherCondition.SUNNY: weather_factor = 1.2
        elif weather == WeatherCondition.RAINY: weather_factor = 0.6
        elif weather == WeatherCondition.STORMY: weather_factor = 0.2

        quality_factor = zoo_quality / 100 # کیفیت باغ وحش (میانگین شادی حیوانات و تمیزی)
        
        new_visitors = int(base_flow * weather_factor * quality_factor * random.uniform(0.8, 1.2))
        
        if self.current_visitors + new_visitors > Config.MAX_ZOO_CAPACITY:
            new_visitors = max(0, Config.MAX_ZOO_CAPACITY - self.current_visitors)

        self.current_visitors += new_visitors
        self.total_visitors_today += new_visitors
        
        income = new_visitors * Config.TICKET_PRICE
        self.revenue_today += income
        
        if new_visitors > 0:
            logger.add_log(f"{new_visitors} بازدیدکننده جدید وارد شدند. درآمد بلیط: {income:,} تومان", "ECONOMY")

    def leave_and_shop(self):
        # بازدیدکنندگان خارج می‌شوند و ممکن است خرید کنند
        leaving = int(self.current_visitors * random.uniform(0.3, 0.7))
        self.current_visitors -= leaving
        
        shop_income = 0
        if self.satisfaction_avg > 70:
            buyers = int(leaving * random.uniform(0.1, 0.3))
            shop_income = buyers * random.randint(50000, 200000) # خرید سوغاتی
            self.revenue_today += shop_income
            
        return leaving, shop_income

    def update_satisfaction(self, zoo: 'Zoo'):
        # محاسبه رضایت بر اساس وضعیت حیوانات و محیط
        total_happiness = sum(a.happiness for enc in zoo.enclosures for a in enc.animals)
        total_cleanliness = sum(enc.cleanliness for enc in zoo.enclosures)
        total_entities = len([a for enc in zoo.enclosures for a in enc.animals]) + len(zoo.enclosures)
        
        if total_entities == 0:
            avg_score = 50
        else:
            avg_score = (total_happiness + total_cleanliness) / total_entities
            
        # نوسان طبیعی
        self.satisfaction_avg = avg_score + random.randint(-5, 5)
        self.satisfaction_avg = max(0, min(100, self.satisfaction_avg))

# ==========================================
# کلاس اصلی باغ وحش (Main Zoo Class)
# ==========================================

class Zoo:
    def __init__(self, name: str):
        self.name = name
        self.money = Config.START_MONEY
        self.day = 1
        self.hour = 8 # شروع کار از ساعت 8 صبح
        self.weather = WeatherCondition.SUNNY
        self.is_night = False
        
        self.enclosures: List[Enclosure] = []
        self.staff: List[StaffMember] = []
        self.visitor_manager = VisitorManager()
        self.visitor_satisfaction_boost = 0

        # راه‌اندازی اولیه
        self._setup_initial_state()

    def _setup_initial_state(self):
        # ساخت محوطه‌ها
        self.enclosures.append(Enclosure(1, "سرزمین شیرها", 4, "ساوانا"))
        self.enclosures.append(Enclosure(2, "جنگل فیل‌ها", 3, "جنگلی"))
        self.enclosures.append(Enclosure(3, "قطب جنوب", 10, "یخی"))
        self.enclosures.append(Enclosure(4, "خانه خزندگان", 8, "بیابانی"))
        self.enclosures.append(Enclosure(5, "باغ پرندگان", 15, "استوایی"))

        # افزودن حیوانات اولیه
        self.add_animal(Lion("سیمبا", 5, "نر"), 1)
        self.add_animal(Lion("نالا", 4, "ماده"), 1)
        self.add_animal(Elephant("بابار", 10, "نر"), 2)
        self.add_animal(Elephant("سلنا", 8, "ماده"), 2)
        self.add_animal(Penguin("پینگو", 3, "نر"), 3)
        self.add_animal(Penguin("پنگا", 3, "ماده"), 3)
        self.add_animal(Snake("کبرا", 6, "نر"), 4)

        # استخدام پرسنل
        self.hire_staff(StaffMember("علی", StaffRole.KEEPER, 8000000))
        self.hire_staff(StaffMember("مریم", StaffRole.VET, 12000000))
        self.hire_staff(StaffMember("رضا", StaffRole.CLEANER, 6000000))
        self.hire_staff(StaffMember("سارا", StaffRole.GUIDE, 7000000))

    def add_animal(self, animal: Animal, enclosure_id: int):
        target_enclosure = next((e for e in self.enclosures if e.id == enclosure_id), None)
        if target_enclosure:
            try:
                target_enclosure.add_animal(animal)
                self.money -= animal.price
                logger.add_log(f"{animal.name} خریداری شد به قیمت {animal.price:,}", "ECONOMY")
            except ValueError as e:
                logger.add_log(str(e), "ERROR")
        else:
            logger.add_log("محوطه یافت نشد.", "ERROR")

    def hire_staff(self, staff: StaffMember):
        self.staff.append(staff)
        logger.add_log(f"{staff.name} به عنوان {staff.role.value} استخدام شد.", "HR")

    def change_weather(self):
        conditions = list(WeatherCondition)
        self.weather = random.choice(conditions)
        logger.add_log(f"آب و هوا تغییر کرد: {self.weather.value}", "SYSTEM")

    def run_simulation_step(self):
        """اجرای یک ساعت از شبیه‌سازی"""
        logger.add_log(f"--- ساعت {self.hour}:00 ---", "TIME")
        
        # 1. بروزرسانی وضعیت حیوانات و محوطه‌ها
        for enc in self.enclosures:
            enc.tick()
            for animal in enc.animals:
                animal.tick(self.weather, self.is_night)

        # 2. فعالیت پرسنل (فقط در ساعات کاری 8 تا 20)
        if 8 <= self.hour <= 20 and not self.is_night:
            for member in self.staff:
                member.work(self)
        elif self.hour == 22:
            # استراحت پرسنل در شب
            for member in self.staff:
                member.rest()

        # 3. مدیریت بازدیدکنندگان
        if 9 <= self.hour <= 18: # ساعات بازدید
            is_weekend = (self.day % 7 == 0) # فرض: هر 7 روز یکبار جمعه است
            self.visitor_manager.simulate_arrival(self.weather, self.get_zoo_quality(), is_weekend)
            self.visitor_manager.update_satisfaction(self)
        elif self.hour == 19:
            # خروج بازدیدکنندگان و تسویه حساب
            left_count, shop_income = self.visitor_manager.leave_and_shop()
            if shop_income > 0:
                logger.add_log(f"فروشگاه هدایا: {shop_income:,} تومان فروش داشت.", "ECONOMY")
            self.visitor_manager.current_visitors = 0 # تخلیه باغ وحش در شب
            self.visitor_manager.satisfaction_avg = 100 # ریست برای فردا

        # 4. پرداخت حقوق (پایان روز ساعت 24)
        if self.hour == 23:
            total_salary = sum(s.salary for s in self.staff) // 30 # حقوق روزانه تقریبی
            self.money -= total_salary
            logger.add_log(f"حقوق روزانه پرسنل کسر شد: {total_salary:,} تومان", "ECONOMY")
            
            # پایان روز
            self.day += 1
            self.hour = 7 # آماده‌سازی برای صبح فردا
            self.change_weather()
            logger.add_log(f"=== روز {self.day-1} به پایان رسید. موجودی بانک: {self.money:,} ===", "DAY_END")
        else:
            self.hour += 1

        # بررسی ورشکستگی
        if self.money < -10000000:
            logger.add_log("باغ وحش ورشکست شد! بازی تمام است.", "GAME_OVER")
            # در نسخه واقعی بازی متوقف می‌شود

    def get_zoo_quality(self) -> int:
        if not self.enclosures: return 50
        total_clean = sum(e.cleanliness for e in self.enclosures) / len(self.enclosures)
        if not any(a for e in self.enclosures for a in e.animals): return int(total_clean)
        total_happy = sum(a.happiness for e in self.enclosures for a in e.animals) / len([a for e in self.enclosures for a in e.animals])
        return int((total_clean + total_happy) / 2)

    def get_full_status_report(self) -> str:
        report = f"\n{'='*40}\nگزارش جامع باغ وحش {self.name}\n{'='*40}\n"
        report += f"روز: {self.day} | ساعت: {self.hour}:00 | آب و هوا: {self.weather.value}\n"
        report += f"موجودی بانک: {self.money:,} تومان\n"
        report += f"بازدیدکنندگان فعلی: {self.visitor_manager.current_visitors}\n"
        report += f"رضایت عمومی: {int(self.visitor_manager.satisfaction_avg)}%\n\n"
        
        report += "--- وضعیت محوطه‌ها و حیوانات ---\n"
        for enc in self.enclosures:
            report += enc.get_status() + "\n"
            for animal in enc.animals:
                report += "   " + animal.get_status_str() + "\n"
        
        report += "\n--- وضعیت پرسنل ---\n"
        for s in self.staff:
            report += f"{s.name} ({s.role.value}): انرژی {s.energy}%\n"
            
        report += f"\n{'='*40}\n"
        return report

# ==========================================
# اجرای اصلی برنامه (Main Execution)
# ==========================================

def main():
    print("در حال بارگذاری شبیه‌ساز باغ وحش هوشمند...")
    time.sleep(1)
    
    zoo = Zoo("باغ وحش ملی ایران")
    
    # نمایش وضعیت اولیه
    print(zoo.get_full_status_report())
    
    # حلقه شبیه‌سازی (اجرای 3 روز کامل برای نمونه)
    # هر روز 24 ساعت است. ما 3 روز را اجرا می‌کنیم.
    total_steps = 24 * 3 
    
    print("\nشروع شبیه‌سازی...\n")
    
    for i in range(total_steps):
        zoo.run_simulation_step()
        # مکث کوتاه برای خوانایی لاگ‌ها در کنسول
        time.sleep(0.1) 
        
        # اگر بازی تمام شد، حلقه را بشکن
        if zoo.money < -10000000:
            break

    # گزارش نهایی
    print("\nپایان شبیه‌سازی نمونه.")
    print(zoo.get_full_status_report())
    
    # ذخیره داده‌ها در فایل JSON (اختیاری)
    data = {
        "day": zoo.day,
        "money": zoo.money,
        "animals_count": sum(len(e.animals) for e in zoo.enclosures),
        "staff_count": len(zoo.staff)
    }
    with open("zoo_save.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("وضعیت در فایل zoo_save.json ذخیره شد.")

if __name__ == "__main__":
    main()
