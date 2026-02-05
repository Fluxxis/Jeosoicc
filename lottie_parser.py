#!/usr/bin/env python3
"""
Telegram Gifts Lottie Parser
Парсер анимаций по имени и цифрам для любого подарка из профиля.
"""

import re
import json
import requests
from typing import Dict, List, Optional, Tuple
import os
import sys

class LottieParser:
    def __init__(self):
        # Словарь соответствий: имя коллекции -> Lottie URL
        self.lottie_map = {
            "Spy Agaric": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQD6mH9bwbn6S3M_tCRWOvqAIW8M34kRwbI01niGLRPeDPsl/ad78888323282bc4",
            "Mousse Cake": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBjzdi27ZI-Re93OOIia0m7YmUU8d8ubJNsStZTc7qNJnOv/02820d81131efef1",
            "Eternal Candle": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBzZLNIr4lie0pTfrbRsANJOtFYwY5gmngRfs84Ras5-aVN/8786ee4a2da53b73",
            "Restless Jar": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDycOgkLwcfPDokh8q-2DIUzVhPetdFuZmwrFYFP6i1nZ_u/c099d698c75b4c30",
            "Stellar Rocket": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDIruSTyxvq60gUH8j2kkj3qzoBrBaJy9WkKbeNNRasWe4j/82cc4259a5d4fadb",
            "Jack-in-the-Box": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQA401QqpXtBnwIaDbFjwd5yXfP2mYiCusbJ3Zcw9eXR9CqL/311b48002dcaceb4",
            "Snoop Dogg": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQAoJw7BpOcBD3y9voMuEQ-qhS3K4gtM-6EePLxkzk8iSifX/4a27bdf126f1c236",
            "Ice Cream": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBUvskEvmWdp_V6HX-2Tyfp4mFSzMzdg9TaUz6zKVz6Ov3f/6963c8bf9186ec4d",
            "Fresh Socks": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQAUffQWl09_yhXDTp8oN13Px8ygPm0xcyNGhHOiONV-x3om/e73575435c843b99",
            "Light Sword": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDRrfw5pgIC4e6NafUAx52Z9Ym6q1k26xxaXR_qx0LKJJ7D/8a2461e92974ec06",
            "Lush Bouquet": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQA2lHcvZWW_bN_2NMKrkEUv9xz6fx8wTE5upa8u1neZb6hJ/1e1733f2e96cf6e8",
            "Top Hat": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQADvJxMxCHA7fRlYjoceBORf7RwKs0rzjVaKepQACMnZzG7/87a4769888f4671c",
            "Holiday Drink": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQB5P3ZP2PjLION52Y1SNAux1do4-ZOqMWotXS-fdMpqHcCH/6214fc78d5135bb3",
            "Input Key": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBSIId7sMmlqN8oBGaMNtUeuaLeSQPUR1ByMwpnfWL3hhZq/d1808ffcf855e5e0",
            "Happy Brownie": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQB1ATaKGNYk6T5R2cA18BOF-KB_idaKKigwYI2jtjWuLg8n/59f712b4b5b578e8",
            "Spring Basket": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCZ4-h65iTiWDPRPcLlS63gbcS40YBadEFLA4W-iIWUZld0/c6aa276254ffb471",
            "Money Pot": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBM3U1twWjI_vYUaPdFkzZs1q9c0orHhQjx0m2Xa9ljgTqY/dbb4f035eb23b761",
            "Khabib’s Papakha": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDsiZuliQn_FTUeyCVaVhojljY7LmimdUtJK1SntGTzff5z/33ea5212813da9aa",
            "Ion Gem": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDL7HMbca0FufrjHFcRoiLkEiOXkXoO_vH2gVUN8JNp4khK/8a18f6cdf272b05c",
            "Desk Calendar": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBMcfMAZlMUr1W3X8kdEw3fJMUAaWH4-XcmE5R5RfFIY0E2/a293182bce065643",
            "Moon Pendant": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQC7oPa-gJDZ6JRwW0WW4WH_Vjn7ioKmfDdFItD7nYFGdbuU/63a6a4dc95adb735",
            "Electric Skull": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQAOYYJib8K6-91TjeOYRbWEtbtRJHXKoWltnULwdaqd7mR5/0f0eb3435a9cfb44",
            "Easter Egg": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQAwnP7dGfE_WO0xiCiulkAXUG1K1bWH1vE1k64T4G-7gruO/45a01eb8ed561c61",
            "Toy Bear": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQC1gud6QO8NdJjVrqr7qFBMO0oQsktkvzhmIRoMKo8vxiyL/fdd58a45af6f6a8c",
            "Big Year": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDx-SqQEhP9Rzfi2cqdehTVUvQbArsUz1X7t-ul8IiKZpYb/245abfb95445b4d4",
            "Candy Cane": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDLM65t0shS7gZAg0lMltGHYhsU94PzsMJHhYibmRV7kdUs/fae3fbc105b9f598",
            "Jester Hat": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCBK_JBASAA5XVz1D17Pn--kQaMWm0b9wReVtsEdRO4Tgy9/38ece3e59365f378",
            "Diamond Ring": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCWh1lPltyTwCWxCXm4umL5tPZoXR8kTIcT-pd0JqoadLHo/e044d118679c0b2c",
            "Bow Tie": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDpxJ6VAwUA-tX6w8ACnoAJLrP3hKWmieBl71uv1_qKRD3x/a8e21d7b62b9ff51",
            "Durov’s Cap": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQD9ikZq6xPgKjzmdBG0G0S80RvUJjbwgHrPZXDKc_wsE84w/774964f1079c7fbe",
            "Hex Pot": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQB6AtBPOuTtQml8oSA7X8ZqJ5QmcOYYqoz92sQYXGUQrxyB/4b8aeefe8db1ce8b_194a95ccd5a",
            "Scared Cat": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQATuUGdvrjLvTWE5ppVFOVCqU2dlCLUnKTsu0n1JYm9la10/7584f0089f1701bd",
            "Evil Eye": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDQ6DjRabTYSAxf2xrZsnsXtqcIm1bj9dF5x_h8lNjWPmH4/a4aba269fe7986d6",
            "Perfume Bottle": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDJsN9OJBhKGZoWZWtkEpzkCfIu16Z9UzTWbYjeLpuHdT5f/f15ea4812d572509",
            "Trapped Heart": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCyAMkb6bNyNlKPH0tJbubk1VVjASqyq9sZwkJ8AbxMkxxU/9587d8a330793106",
            "Skull Flower": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBaOL8mH5YywkXjkps65X1OLPNH7pns4YcfLmaVpFaoNKZn/6e1f4f7c0b206b03_194a967c648",
            "Plush Pepe": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBG-g6ahkAUGWpefWbx-D_9sQ8oWbvy6puuq78U2c4NUDFS/1e2b8edb5ca3bf71_194a96db50b",
            "Spiced Wine": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQA8DCWyCWyywgOKYORerRoSVevWrUQ_FjKQgNihxY1227x7/7b493d15df351e09",
            "Precious Peach": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQA4i58iuS9DUYRtUZ97sZo5mnkbiYUBpWXQOe3dEUCcP1W8/a3ac863e85872512",
            "Sharp Tongue": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBw2tO5UaJ4c_YXt3I8y5KD0k37staZxedV2O5HmryiK0dN/0eb50d6e7b9b822c_194a970f43d",
            "Jelly Bunny": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQAwzubeoJwnqmmBuTPpnUSurRzWPB8ERzcfzx55Z2YjE0jx/6a9d8347ca00a1bc",
            "Signet Ring": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCrGA9slCoksgD-NyRDjtHySKN0Ts8k6hdueJkUkZZdD4_K/f45025599e91afd7_194a978e47c",
            "Xmas Stocking": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDz_VecErEBTLOTiR1tq0VS3lZuHHqhYmhZbthcrbFk7ztK/3fde93225df39441",
            "Snake Box": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBbUKx5CalEly2TekDNeFbv4e02pj6xsAqXZP0X_AprKj4I/5f878babe7aa5692",
            "Party Sparkler": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCa1I09fE9UoTV6awM6QC9-fkv51hoii24w1tJoFfigG_ax/d425bb0123a64bd0",
            "Lol Pop": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQC6zjid8vJNEWqcXk10XjsdDLRKbcPZzbHusuEW6FokOWIm/6557a42394a777d1",
            "Valentine Box": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDjBdu3zS-JT94OwIup4KVNaQjxDzGcIPRJ24Ha0Y8jLw83/5360e6ef35aefa3e",
            "Whip Cupcake": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQAo_snApDDqF6GKV0xe_T5oe28r842gJtgmkgPMhX0-dRkh/c205b7f732cce65a",
            "Snoop Cigar": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQA72Uevr_MHvzYwSCHJUK-uC6kd-w8kbxzhJ49WIiG-o6CD/3687a49c80ea2070",
            "B-Day Candle": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCwEFfUbbR-22fn3VgxUpBil7bwBQqEHm7wgQYbWY9c08YJ/beeaea3af4db4301",
            "Witch Hat": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBD8aBKC4NsnYMqtkCfPQk2EVnieynJQp1UgZVyx1VmR5Ml/e72cf96d2737fa03",
            "Sleigh Bell": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBcNxMCTyEHkcQ5cK3fO_3Ebjf6JcA5JJ_OJV4npDN-604P/cf9fb31b73343828",
            "Lunar Snake": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQC2lsUy1SKxJEJBwj5ZCfVnLPvAqDqy5c26Xg8xS_pDTXGk/115b15bf39802048",
            "Homemade Cake": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCefrjhCD2_7HRIr2lmwt9ZaqeG_tdseBvADC66833kBS3y/62b580ec6ff29cd5",
            "UFC Strike": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDaj18cd61VLZHCHsM7sKbfxBudD3gaSfcN02olVnQ3BCIB/33e6cd821fc23cbd",
            "Tama Gadget": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQA_kx2WOydXWzYUYO1DP80aHl4yhlLGYhxjPAtRPNjMgfYM/0f1a258094ad64c3",
            "Kissed Frog": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDTro-ogJbS7o-OBD6bt2NysPt7SnGm5zfuRXGB1nE_rbGa/2edec879d4a6877d",
            "Jolly Chimp": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCeTSJOPXP_SSvOjILY-kui4bGHUmsa-U7TXP4DjUANTl4s/be41491b0ba88313",
            "Love Potion": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQD7yDu2WCgd9Uzx1dF_DQkWK7IZJJ4Mp9M9g1rGUUiQE43m/17f15f9e3d757ee8",
            "Magic Potion": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQAtFU9GrGfix4UG9DOivN58QxvgBJUaAZ_pdZBZCmbhKo4P/4b5a3e64f520fb91",
            "Ionic Dryer": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQCEVLBbgzL5Ih9bzMkneLi68xzOelYN3NEugm_4gZTpuAFP/079740bed9b9810c",
            "Low Rider": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQDCPq7QSUvCmq7kBhmDulxVdeFHKFc1wT9MQxnesanl1Hql/a6cd14f02c34966b",
            "Berry Box": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQB4x3sT1DVdODzay3H-4VJIdOooS5-kTgyKcYMZWogPOsiq/f64cb1a58102a3e8_194a95c968f",
            "Vintage Cigar": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQACcQpR2fmdeENWdE2YGQWHVxSTyA8Zq4_k7rk_IaxCRXNe/c8f476a6e2695621",
            "Cookie Heart": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQBT9PbZBR6FGcZBSnwgo-DLpc0r7_X_8dlhG5UA6v9l9uJM/53194740c87fef10",
            "Bunny Muffin": "https://ddejfvww7sqtk.cloudfront.net/nft-content-cache/lottie/EQA3-i1IUFjWyDhaIoCGdYUB4nt2IYaT3T-95CHPrSvV3AfX/cf2feaca0c08096f"
        }

    def parse_gift_name(self, gift_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Парсит имя подарка и возвращает имя коллекции и номер.
        Примеры:
            "Spy Agaric #27641" -> ("Spy Agaric", "27641")
            "Mousse Cake #40311" -> ("Mousse Cake", "40311")
            "Big Year #123" -> ("Big Year", "123")
        """
        # Регулярное выражение для поиска имени и номера
        pattern = r'^(.+?)\s*#\s*(\d+)$'
        match = re.match(pattern, gift_name.strip())
        
        if match:
            collection_name = match.group(1).strip()
            number = match.group(2)
            return collection_name, number
        else:
            # Если не удалось распарсить, возвращаем None
            return None, None

    def get_lottie_url(self, collection_name: str) -> Optional[str]:
        """
        Возвращает Lottie URL по имени коллекции.
        """
        # Сначала пробуем точное совпадение
        if collection_name in self.lottie_map:
            return self.lottie_map[collection_name]
        
        # Если не нашли, пробуем найти по части имени (без пробелов)
        # Например: "SpyAgaric" -> "Spy Agaric"
        for key in self.lottie_map:
            if key.replace(" ", "") == collection_name.replace(" ", ""):
                return self.lottie_map[key]
        
        # Если всё равно не нашли, возвращаем None
        return None

    def generate_lottie_html(self, lottie_url: str, autoplay: bool = False, loop: bool = False) -> str:
        """
        Генерирует HTML для встраивания Lottie анимации.
        """
        attrs = [
            f'src="{lottie_url}"',
            'background="transparent"',
            'speed="1"',
            'preserveAspectRatio="xMidYMid slice"'
        ]
        
        if autoplay:
            attrs.append('autoplay')
        if loop:
            attrs.append('loop')
        
        return f'<lottie-player {" ".join(attrs)} style="width:100%; height:100%;"></lottie-player>'

    def process_gift(self, gift_name: str, autoplay: bool = False, loop: bool = False) -> Dict:
        """
        Полностью обрабатывает имя подарка и возвращает данные для отображения.
        """
        collection_name, number = self.parse_gift_name(gift_name)
        
        if not collection_name:
            return {
                "success": False,
                "error": f"Не удалось распарсить имя подарка: '{gift_name}'",
                "gift_name": gift_name,
                "collection_name": None,
                "number": None,
                "lottie_url": None,
                "html": None
            }
        
        lottie_url = self.get_lottie_url(collection_name)
        
        if not lottie_url:
            return {
                "success": False,
                "error": f"Анимация для коллекции '{collection_name}' не найдена",
                "gift_name": gift_name,
                "collection_name": collection_name,
                "number": number,
                "lottie_url": None,
                "html": None
            }
        
        html = self.generate_lottie_html(lottie_url, autoplay=autoplay, loop=loop)
        
        return {
            "success": True,
            "gift_name": gift_name,
            "collection_name": collection_name,
            "number": number,
            "lottie_url": lottie_url,
            "html": html
        }

    def add_collection(self, collection_name: str, lottie_url: str):
        """
        Добавляет новую коллекцию в словарь.
        """
        self.lottie_map[collection_name] = lottie_url

    def get_all_collections(self) -> List[str]:
        """
        Возвращает список всех известных коллекций.
        """
        return list(self.lottie_map.keys())

    def save_to_file(self, filename: str = "lottie_map.json"):
        """
        Сохраняет словарь коллекций в JSON файл.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.lottie_map, f, indent=2, ensure_ascii=False)

    def load_from_file(self, filename: str = "lottie_map.json"):
        """
        Загружает словарь коллекций из JSON файла.
        """
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.lottie_map.update(json.load(f))

def main():
    parser = LottieParser()
    
    # Примеры использования
    test_gifts = [
        "Spy Agaric #27641",
        "Mousse Cake #40311",
        "Eternal Candle #7856",
        "Restless Jar #1732",
        "Stellar Rocket #77564",
        "Jack-in-the-Box #1287",
        "Snoop Dogg #306168",
        "Ice Cream #33019",
        "Fresh Socks #5340",
        "Light Sword #25087",
        "Lush Bouquet #4315",
        "Top Hat #11048",
        "Holiday Drink #22200",
        "Input Key #66374",
        "Happy Brownie #101299",
        "Spring Basket #18731",
        "Money Pot #25433",
        "Spring Basket #61462",
        "Mousse Cake #78867",
        "Instant Ramen #337835",
        "Input Key #78219",
        "Khabib’s Papakha #13209",
        "Spring Basket #3249",
        "Happy Brownie #2334",
        "Ion Gem #1",
        "Desk Calendar #1",
        "Moon Pendant #2",
        "Electric Skull #2",
        "Easter Egg #3",
        "Toy Bear #3",
        "Big Year #3",
        "Candy Cane #4",
        "Jester Hat #4",
        "Diamond Ring #4",
        "Big Year #4",
        "Bow Tie #5",
        "Spy Agaric #7",
        "Spy Agaric #386",
        "Durov’s Cap #255",
        "Hex Pot #4268",
        "Scared Cat #7",
        "Scared Cat #652",
        "Evil Eye #9897",
        "Santa Hat #4229",
        "Santa Hat #385",
        "Perfume Bottle #486",
        "Spy Agaric #10250",
        "Trapped Heart #244",
        "Skull Flower #5987",
        "Durov’s Cap #204",
        "Plush Pepe #1194",
        "Trapped Heart #2003",
        "Durov’s Cap #1444",
        "Spiced Wine #8057",
        "Santa Hat #2068",
        "Durov’s Cap #714",
        "Precious Peach #45",
        "Sharp Tongue #3735",
        "Spy Agaric #1048",
        "Jelly Bunny #844",
        "Durov’s Cap #811",
        "Signet Ring #151",
        "Evil Eye #2108",
        "Trapped Heart #49",
        "Sharp Tongue #1168",
        "Evil Eye #12802",
        "Spy Agaric #20945",
        "Durov’s Cap #673",
        "Durov’s Cap #722",
        "Skull Flower #45",
        "Sharp Tongue #1096",
        "Spy Agaric #5520",
        "Durov’s Cap #2558",
        "Durov’s Cap #660",
        "Magic Potion #1157",
        "Hex Pot #4119",
        "Magic Potion #1375",
        "Spy Agaric #20946",
        "B-Day Candle #138345",
        "Instant Ramen #144702",
        "Spring Basket #61462",
        "Mousse Cake #78867",
        "Xmas Stocking #48335",
        "Light Sword #10732",
        "Instant Ramen #61148",
        "Input Key #117029",
        "Xmas Stocking #49842",
        "Pet Snake #49367",
        "Bow Tie #19767",
        "Instant Ramen #337835",
        "Spring Basket #40436",
        "Instant Ramen #237764",
        "Stellar Rocket #16998",
        "Money Pot #5520",
        "Input Key #78219",
        "Spring Basket #3249",
        "Instant Ramen #31123",
        "Holiday Drink #39721",
        "Spring Basket #13321",
        "Mousse Cake #74402",
        "Eternal Candle #13035",
        "Happy Brownie #2334",
        "Lush Bouquet #17999",
        "Desk Calendar #83356",
        "Happy Brownie #65737",
        "Money Pot #21151",
        "Lol Pop #223387",
        "Holiday Drink #37790",
        "Money Pot #3413",
        "Lol Pop #391248",
        "Spring Basket #51766",
        "Happy Brownie #893",
        "Xmas Stocking #50773",
        "Light Sword #74621",
        "Whip Cupcake #79613",
        "Snake Box #9804",
        "Party Sparkler #33439",
        "Xmas Stocking #16018",
        "Xmas Stocking #21971",
        "Whip Cupcake #41868",
        "Lol Pop #147748",
        "Valentine Box #14448",
        "Whip Cupcake #10020",
        "Big Year #21435",
        "Sleigh Bell #2124",
        "Lunar Snake #6450",
        "Spring Basket #51766",
        "Instant Ramen #268537",
        "Light Sword #16385",
        "Stellar Rocket #4670",
        "Ice Cream #32207",
        "Ice Cream #11990",
        "Big Year #43069",
        "Party Sparkler #33439",
        "Snoop Cigar #66262",
        "Instant Ramen #177764",
        "B-Day Candle #213851",
        "Lush Bouquet #17999",
        "Happy Brownie #65737",
        "Spy Agaric #16078",
        "Holiday Drink #476",
        "Eternal Candle #13035",
        "Light Sword #64130",
        "Spy Agaric #12494",
        "Lol Pop #147748",
        "Happy Brownie #54791",
        "Desk Calendar #83356",
        "Money Pot #3413",
        "Whip Cupcake #79613",
        "Snoop Dogg #380303",
        "Ice Cream #52575",
        "Lol Pop #6233",
        "Happy Brownie #90268",
        "Hex Pot #1403",
        "Lol Pop #30090",
        "Spiced Wine #520",
        "Lol Pop #63494",
        "Money Pot #38349",
        "Happy Brownie #2334",
        "Hex Pot #24588",
        "Winter Wreath #4649",
        "Lol Pop #97718",
        "Happy Brownie #60291",
        "Happy Brownie #171936",
        "Whip Cupcake #41868",
        "Snake Box #8684",
        "Lol Pop #223387",
        "Snoop Cigar #55523",
        "Snoop Dogg #221815",
        "Xmas Stocking #16018",
        "Snoop Dogg #30937",
        "Holiday Drink #37790",
        "Happy Brownie #893",
        "Lol Pop #29976",
        "Mousse Cake #74402",
        "Input Key #12448",
        "Money Pot #21151",
        "Spy Agaric #367",
        "Hex Pot #8580",
        "Lol Pop #20928",
        "Spy Agaric #14336",
        "Stellar Rocket #121829",
        "Pet Snake #14813",
        "Xmas Stocking #50773",
        "Winter Wreath #46402",
        "Xmas Stocking #21971",
        "Stellar Rocket #93416",
        "Lol Pop #156320",
        "Desk Calendar #42150",
        "Witch Hat #31558",
        "Valentine Box #14448",
        "Holiday Drink #20375",
        "Spy Agaric #31048",
        "Jack-in-the-Box #83020",
        "Light Sword #74621",
        "Whip Cupcake #10020",
        "Snake Box #9804",
        "Input Key #59919",
        "Lol Pop #391248",
        "Happy Brownie #55694",
        "Ice Cream #223926",
        "Ice Cream #60895",
        "Snoop Cigar #78282",
        "Happy Brownie #45357",
        "Happy Brownie #69809",
        "Sleigh Bell #9000",
        "Spring Basket #28558",
        "Spy Agaric #40638",
        "Mousse Cake #64759",
        "Jack-in-the-Box #45942",
        "Snoop Cigar #33771",
        "Money Pot #31145",
        "Perfume Bottle #2666",
        "Money Pot #10356",
        "Love Potion #20018",
        "Trapped Heart #17339",
        "Ice Cream #288922",
        "Money Pot #11958",
        "Low Rider #22865",
        "Money Pot #4915",
        "Money Pot #60015",
        "Mousse Cake #26110",
        "Ice Cream #254115",
        "Cookie Heart #41591",
        "UFC Strike #45734",
        "Ice Cream #206529",
        "Money Pot #51264",
        "Money Pot #28912",
        "Ice Cream #165306",
        "Top Hat #7529",
        "Money Pot #12644",
        "Snoop Cigar #15971",
        "Trapped Heart #15398",
        "Money Pot #16868",
        "Input Key #18643",
        "Money Pot #20209",
        "Desk Calendar #173861",
        "Money Pot #2296",
        "Homemade Cake #159905",
        "Money Pot #58832",
        "UFC Strike #47238",
        "Money Pot #8387",
        "Ice Cream #230226",
        "Money Pot #6338",
        "Spy Agaric #5126",
        "Money Pot #17776",
        "Money Pot #27904",
        "Ice Cream #243172",
        "Diamond Ring #13270",
        "Money Pot #14595",
        "Ice Cream #100198",
        "Ice Cream #25190",
        "Love Potion #11585",
        "Money Pot #15218",
        "Ionic Dryer #4766",
        "UFC Strike #47231",
        "Spy Agaric #74323",
        "Homemade Cake #162124",
        "Money Pot #39174",
        "Money Pot #7413",
        "Desk Calendar #141728",
        "Money Pot #24497",
        "Money Pot #59329",
        "Tama Gadget #44464",
        "Desk Calendar #315440",
        "Money Pot #55460",
        "Bunny Muffin #19570",
        "Money Pot #46309",
        "Ice Cream #125331",
        "Ice Cream #175801",
        "Homemade Cake #162109",
        "Money Pot #2476",
        "Jack-in-the-Box #77608",
        "Ice Cream #156102",
        "Money Pot #10684",
        "Snoop Cigar #61737",
        "Ice Cream #116318",
        "Mousse Cake #57447",
        "Jack-in-the-Box #8038",
        "Jack-in-the-Box #43576",
        "Ice Cream #11393",
        "Snoop Cigar #110954",
        "Snoop Cigar #95753",
        "Jolly Chimp #27289",
        "Ice Cream #93308",
        "Ice Cream #206809",
        "Homemade Cake #91685",
        "Ion Gem #3781",
        "Mousse Cake #117650",
        "Berry Box #1569",
        "Spy Agaric #30240",
        "Evil Eye #1673",
        "Spy Agaric #28151",
        "Jelly Bunny #3863",
        "Trapped Heart #930",
        "Spiced Wine #2578",
        "Evil Eye #7279",
        "Trapped Heart #6061",
        "Plush Pepe #1383",
        "Evil Eye #17704",
        "Signet Ring #5648",
        "Trapped Heart #2196",
        "Trapped Heart #865",
        "Spy Agaric #28154",
        "Jelly Bunny #6219",
        "Spiced Wine #2603",
        "Durov’s Cap #498",
        "Spy Agaric #24800",
        "Spy Agaric #29492",
        "Jelly Bunny #1741",
        "Durov’s Cap #2662",
        "Skull Flower #125",
        "Evil Eye #17337",
        "Vintage Cigar #2964",
        "Trapped Heart #3905",
        "Sharp Tongue #1521",
        "Santa Hat #2059",
        "Signet Ring #5638",
        "Magic Potion #164",
        "Spy Agaric #7618",
        "Spy Agaric #13024",
        "Spy Agaric #1028",
        "Kissed Frog #478",
        "Durov’s Cap #2525",
        "Santa Hat #2986",
        "Trapped Heart #4220",
        "Sharp Tongue #706",
        "Skull Flower #666",
        "Signet Ring #741",
        "Evil Eye #2540",
        "Spiced Wine #6396",
        "Spy Agaric #5226",
        "Hex Pot #10396",
        "Spy Agaric #13057",
        "Evil Eye #5270",
        "Spy Agaric #12716",
        "Trapped Heart #5927",
        "Spy Agaric #30238",
        "Skull Flower #686",
        "Hex Pot #14345",
        "Spy Agaric #1040",
        "Hex Pot #1731",
        "Spy Agaric #265",
        "Spiced Wine #2617",
        "Spy Agaric #12722",
        "Homemade Cake #2672",
        "Vintage Cigar #2673",
        "Skull Flower #1738",
        "Hex Pot #3596",
        "Spiced Wine #1746",
        "Skull Flower #5808",
        "Perfume Bottle #1810",
        "Jelly Bunny #2521",
        "Spy Agaric #24856",
        "Spy Agaric #30241",
        "Spy Agaric #7584",
        "Spy Agaric #20874",
        "Homemade Cake #4784",
        "Spy Agaric #30242",
        "Homemade Cake #1683",
        "Spy Agaric #4054",
        "Homemade Cake #4742",
        "Signet Ring #4269",
        "Vintage Cigar #4847",
        "Vintage Cigar #2669",
        "Spiced Wine #7641",
        "Signet Ring #2512",
        "Spy Agaric #7577",
        "Evil Eye #230",
        "Signet Ring #2136",
        "Magic Potion #274",
        "Sharp Tongue #2786",
        "Evil Eye #17335"
    ]

    print("=== Telegram Gifts Lottie Parser ===\n")
    print(f"Всего коллекций в базе: {len(parser.get_all_collections())}")
    print(f"Всего тестовых подарков: {len(test_gifts)}\n")

    success_count = 0
    failed_count = 0

    for gift in test_gifts:
        result = parser.process_gift(gift)
        
        if result["success"]:
            success_count += 1
            print(f"✅ {gift}")
            print(f"   Коллекция: {result['collection_name']}")
            print(f"   Номер: {result['number']}")
            print(f"   URL: {result['lottie_url'][:80]}...")
        else:
            failed_count += 1
            print(f"❌ {gift}")
            print(f"   Ошибка: {result['error']}")
        
        print()

    print(f"=== Статистика ===")
    print(f"✅ Успешно обработано: {success_count}")
    print(f"❌ Ошибок: {failed_count}")
    print(f"📊 Процент успеха: {success_count / len(test_gifts) * 100:.1f}%")

    # Сохранение словаря в файл
    parser.save_to_file()
    print(f"\n💾 Словарь сохранён в файл: lottie_map.json")

if __name__ == "__main__":
    main()
lottie_parser = LottieParser()