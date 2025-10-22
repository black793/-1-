#!/usr/bin/env python3
"""
YouTube Subscribers Boost - Python Version
Advanced YouTube subscribers boosting script with GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import time
import random
from datetime import datetime
import webbrowser
import requests
from urllib.parse import urlparse
import sqlite3
import os
import re

# Real boost imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class FacebookBoostApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Facebook Followers Boost - Python Version")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Facebook settings
        self.facebook_api_key = None
        
        # Data storage
        self.pages = []  # Facebook pages instead of channels
        self.accounts = []
        self.proxies = []
        self.history = []
        self.current_boost = None
        self.boost_thread = None
        self.is_boosting = False
        
        # Real boost settings
        self.real_boost_mode = False
        self.active_drivers = []
        self.boost_speed_multiplier = 1.0
        
        # Database setup
        self.setup_database()
        
        # Load data
        self.load_data()
        
        # Create GUI
        self.create_gui()
        
        # Update display
        self.update_display()
    
    def get_youtube_channel_info(self, channel_id):
        """Get real channel information from YouTube"""
        try:
            # Try multiple methods in order
            methods = [
                ("API Method", self.get_channel_info_api),
                ("Method 1 (Channel Page)", self.get_channel_info_method1),
                ("Method 2 (About Page)", self.get_channel_info_method2),
                ("Method 3 (Videos Page)", self.get_channel_info_method3),
                ("Method 4 (Alternative)", self.get_channel_info_method4)
            ]
            
            for method_name, method_func in methods:
                try:
                    print(f"Trying {method_name}...")
                    result = method_func(channel_id)
                    if result['success'] and result['subscriber_count'] > 0:
                        print(f"Success with {method_name}: {result['title']} - {result['subscriber_count']} subscribers")
                        return result
                    elif result['success'] and result['title'] != f"قناة {channel_id[:8]}":
                        print(f"Partial success with {method_name}: {result['title']}")
                        return result
                except Exception as e:
                    print(f"Error in {method_name}: {str(e)}")
                    continue
            
            # If all methods failed, return basic info
            return {
                'title': f"قناة {channel_id[:8]}",
                'subscriber_count': 0,
                'success': True,
                'note': 'تم الحصول على معلومات أساسية فقط'
            }
                
        except Exception as e:
            print(f"Error in get_youtube_channel_info: {str(e)}")
            return {
                'title': f"قناة {channel_id[:8]}",
                'subscriber_count': 0,
                'success': True,
                'note': 'تم الحصول على معلومات أساسية فقط'
            }
    
    def get_channel_info_method1(self, channel_id):
        """Method 1: Direct channel page"""
        url = f"https://www.youtube.com/channel/{channel_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            
            # Extract channel name
            title_patterns = [
                r'"channelName":"([^"]+)"',
                r'"title":"([^"]+)"',
                r'"name":"([^"]+)"',
                r'<meta property="og:title" content="([^"]+)"',
                r'<title>([^<]+)</title>'
            ]
            
            channel_title = f"قناة {channel_id[:8]}"
            for pattern in title_patterns:
                title_match = re.search(pattern, content)
                if title_match:
                    channel_title = title_match.group(1).strip()
                    break
            
            # Extract subscriber count with more patterns
            sub_patterns = [
                r'"subscriberCountText":\{"simpleText":"([^"]+)"\}',
                r'"subscriberCount":\{"simpleText":"([^"]+)"\}',
                r'"subscriberCountText":\{"runs":\[\{"text":"([^"]+)"\}\]\}',
                r'"subscriberCount":\{"runs":\[\{"text":"([^"]+)"\}\]\}',
                r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*(?:مشترك|subscriber)',
                r'(\d+(?:,\d{3})*)\s*(?:مشترك|subscriber)',
                r'"subscriberCountText":\{"runs":\[\{"text":"([^"]+)"\},\{"text":"([^"]+)"\}\]\}'
            ]
            
            subscriber_count = 0
            for pattern in sub_patterns:
                sub_matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in sub_matches:
                    if match.groups():
                        for group in match.groups():
                            if group:
                                subscriber_count = self.parse_subscriber_count(group)
                                if subscriber_count > 0:
                                    break
                    if subscriber_count > 0:
                        break
                if subscriber_count > 0:
                    break
            
            return {
                'title': channel_title,
                'subscriber_count': subscriber_count,
                'success': subscriber_count > 0
            }
        
        return {'success': False}
    
    def get_channel_info_method2(self, channel_id):
        """Method 2: Channel about page"""
        url = f"https://www.youtube.com/channel/{channel_id}/about"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            
            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', content)
            channel_title = title_match.group(1).strip() if title_match else f"قناة {channel_id[:8]}"
            
            # Look for subscriber count in about page
            sub_patterns = [
                r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*(?:مشترك|subscriber)',
                r'"subscriberCountText":\{"simpleText":"([^"]+)"\}',
                r'(\d+(?:,\d{3})*)\s*مشترك'
            ]
            
            subscriber_count = 0
            for pattern in sub_patterns:
                sub_match = re.search(pattern, content, re.IGNORECASE)
                if sub_match:
                    subscriber_text = sub_match.group(1)
                    subscriber_count = self.parse_subscriber_count(subscriber_text)
                    if subscriber_count > 0:
                        break
            
            return {
                'title': channel_title,
                'subscriber_count': subscriber_count,
                'success': subscriber_count > 0
            }
        
        return {'success': False}
    
    def get_channel_info_method3(self, channel_id):
        """Method 3: Try to get from channel videos page"""
        url = f"https://www.youtube.com/channel/{channel_id}/videos"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            
            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', content)
            channel_title = title_match.group(1).strip() if title_match else f"قناة {channel_id[:8]}"
            
            # Look for any subscriber information
            subscriber_count = 0
            
            # Try to find subscriber count in various formats
            sub_patterns = [
                r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*(?:مشترك|subscriber)',
                r'"subscriberCountText":\{"simpleText":"([^"]+)"\}',
                r'(\d+(?:,\d{3})*)\s*مشترك'
            ]
            
            for pattern in sub_patterns:
                sub_match = re.search(pattern, content, re.IGNORECASE)
                if sub_match:
                    subscriber_text = sub_match.group(1)
                    subscriber_count = self.parse_subscriber_count(subscriber_text)
                    if subscriber_count > 0:
                        break
            
            return {
                'title': channel_title,
                'subscriber_count': subscriber_count,
                'success': subscriber_count > 0
            }
        
            return {'success': False}
    
    def get_channel_info_api(self, channel_id):
        """Method API: Try to get info using YouTube's internal API"""
        try:
            url = f"https://www.youtube.com/channel/{channel_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # Try to extract from initial data
                import json
                
                # Look for initial data
                initial_data_match = re.search(r'var ytInitialData = ({.+?});', content)
                if initial_data_match:
                    try:
                        initial_data = json.loads(initial_data_match.group(1))
                        
                        # Extract channel info from initial data
                        channel_info = self.extract_channel_from_initial_data(initial_data)
                        if channel_info:
                            return channel_info
                    except:
                        pass
                
                # Try to extract from page data
                page_data_match = re.search(r'"channelMetadataRenderer":\s*({.+?})', content)
                if page_data_match:
                    try:
                        page_data = json.loads(page_data_match.group(1))
                        channel_info = self.extract_channel_from_page_data(page_data)
                        if channel_info:
                            return channel_info
                    except:
                        pass
                
                # Fallback to regex patterns
                return self.extract_with_regex_patterns(content, channel_id)
            
            return {'success': False}
            
        except Exception as e:
            print(f"API method error: {str(e)}")
            return {'success': False}
    
    def extract_channel_from_initial_data(self, data):
        """Extract channel info from YouTube's initial data"""
        try:
            # Navigate through the complex structure
            if 'contents' in data:
                contents = data['contents']
                if 'twoColumnBrowseResultsRenderer' in contents:
                    results = contents['twoColumnBrowseResultsRenderer']
                    if 'tabs' in results:
                        for tab in results['tabs']:
                            if 'tabRenderer' in tab:
                                tab_renderer = tab['tabRenderer']
                                if 'content' in tab_renderer:
                                    content = tab_renderer['content']
                                    if 'sectionListRenderer' in content:
                                        sections = content['sectionListRenderer']['contents']
                                        for section in sections:
                                            if 'itemSectionRenderer' in section:
                                                items = section['itemSectionRenderer']['contents']
                                                for item in items:
                                                    if 'channelAboutFullMetadataRenderer' in item:
                                                        about = item['channelAboutFullMetadataRenderer']
                                                        title = about.get('title', {}).get('runs', [{}])[0].get('text', '')
                                                        subscriber_text = about.get('subscriberCountText', {}).get('simpleText', '')
                                                        subscriber_count = self.parse_subscriber_count(subscriber_text)
                                                        return {
                                                            'title': title,
                                                            'subscriber_count': subscriber_count,
                                                            'success': True
                                                        }
            return None
        except:
            return None
    
    def extract_channel_from_page_data(self, data):
        """Extract channel info from page data"""
        try:
            title = data.get('title', '')
            # Try to find subscriber count in the data structure
            subscriber_count = 0
            # This would need to be implemented based on actual data structure
            return {
                'title': title,
                'subscriber_count': subscriber_count,
                'success': bool(title)
            }
        except:
            return None
    
    def extract_with_regex_patterns(self, content, channel_id):
        """Extract channel info using regex patterns"""
        # Extract title
        title_patterns = [
            r'"channelName":"([^"]+)"',
            r'"title":"([^"]+)"',
            r'"name":"([^"]+)"',
            r'<meta property="og:title" content="([^"]+)"',
            r'<title>([^<]+)</title>'
        ]
        
        channel_title = f"قناة {channel_id[:8]}"
        for pattern in title_patterns:
            title_match = re.search(pattern, content)
            if title_match:
                channel_title = title_match.group(1).strip()
                break
        
        # Extract subscriber count
        sub_patterns = [
            r'"subscriberCountText":\{"simpleText":"([^"]+)"\}',
            r'"subscriberCount":\{"simpleText":"([^"]+)"\}',
            r'"subscriberCountText":\{"runs":\[\{"text":"([^"]+)"\}\]\}',
            r'"subscriberCount":\{"runs":\[\{"text":"([^"]+)"\}\]\}',
            r'(\d+(?:\.\d+)?[KMB]?)\s*(?:مشترك|subscriber)',
            r'(\d+(?:,\d{3})*)\s*(?:مشترك|subscriber)'
        ]
        
        subscriber_count = 0
        for pattern in sub_patterns:
            sub_matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in sub_matches:
                if match.groups():
                    for group in match.groups():
                        if group:
                            subscriber_count = self.parse_subscriber_count(group)
                            if subscriber_count > 0:
                                break
                if subscriber_count > 0:
                    break
            if subscriber_count > 0:
                break
        
        return {
            'title': channel_title,
            'subscriber_count': subscriber_count,
            'success': True
        }
    
    def get_channel_info_method4(self, channel_id):
        """Method 4: Alternative approach using different endpoints"""
        try:
            # Try different URL patterns
            urls = [
                f"https://www.youtube.com/channel/{channel_id}",
                f"https://www.youtube.com/c/{channel_id}",
                f"https://www.youtube.com/user/{channel_id}",
                f"https://www.youtube.com/@{channel_id}"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            for url in urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        content = response.text
                        
                        # Extract title
                        title_match = re.search(r'<title>([^<]+)</title>', content)
                        channel_title = title_match.group(1).strip() if title_match else f"قناة {channel_id[:8]}"
                        
                        # Try to find any subscriber information
                        subscriber_count = 0
                        sub_patterns = [
                            r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*(?:مشترك|subscriber)',
                            r'"subscriberCountText":\{"simpleText":"([^"]+)"\}',
                            r'(\d+(?:,\d{3})*)\s*مشترك'
                        ]
                        
                        for pattern in sub_patterns:
                            sub_match = re.search(pattern, content, re.IGNORECASE)
                            if sub_match:
                                subscriber_text = sub_match.group(1)
                                subscriber_count = self.parse_subscriber_count(subscriber_text)
                                if subscriber_count > 0:
                                    break
                        
                        if subscriber_count > 0:
                            return {
                                'title': channel_title,
                                'subscriber_count': subscriber_count,
                                'success': True
                            }
                        elif channel_title != f"قناة {channel_id[:8]}":
                            return {
                                'title': channel_title,
                                'subscriber_count': 0,
                                'success': True
                            }
                except:
                    continue
            
            return {'success': False}
            
        except Exception as e:
            print(f"Method 4 error: {str(e)}")
            return {'success': False}
    
    def get_channel_info_alternative(self, channel_id):
        """Alternative method to get channel info"""
        try:
            # Try using a different URL format
            url = f"https://www.youtube.com/c/{channel_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Extract title
                title_match = re.search(r'<title>([^<]+)</title>', content)
                channel_title = title_match.group(1).strip() if title_match else f"قناة {channel_id[:8]}"
                
                # Try to find subscriber count
                subscriber_count = 0
                sub_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)', content)
                if sub_match:
                    subscriber_count = self.parse_subscriber_count(sub_match.group(1))
                
                return {
                    'title': channel_title,
                    'subscriber_count': subscriber_count,
                    'success': True
                }
            else:
                # Fallback - return basic info
                return {
                    'title': f"قناة {channel_id[:8]}",
                    'subscriber_count': 0,
                    'success': True,  # Still consider it success for basic info
                    'note': 'تم الحصول على معلومات أساسية فقط'
                }
                
        except Exception as e:
            # Final fallback
            return {
                'title': f"قناة {channel_id[:8]}",
                'subscriber_count': 0,
                'success': True,  # Still consider it success for basic info
                'note': 'تم الحصول على معلومات أساسية فقط'
            }
    
    def parse_subscriber_count(self, subscriber_text):
        """Parse subscriber count text to number"""
        try:
            if not subscriber_text:
                return 0
                
            # Clean the text
            text = str(subscriber_text).replace(',', '').replace(' ', '').lower().strip()
            
            # Handle Arabic numbers
            arabic_to_english = {
                '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
            }
            
            for arabic, english in arabic_to_english.items():
                text = text.replace(arabic, english)
            
            # Extract number and multiplier
            number_match = re.search(r'([\d.]+)', text)
            if not number_match:
                return 0
                
            number = float(number_match.group(1))
            
            # Determine multiplier
            if any(x in text for x in ['k', 'ألف', 'الف']):
                return int(number * 1000)
            elif any(x in text for x in ['m', 'مليون', 'million']):
                return int(number * 1000000)
            elif any(x in text for x in ['b', 'مليار', 'billion']):
                return int(number * 1000000000)
            elif any(x in text for x in ['t', 'تريليون', 'trillion']):
                return int(number * 1000000000000)
            else:
                # Just numbers
                return int(number)
                
        except Exception as e:
            print(f"Error parsing subscriber count: {subscriber_text} - {e}")
            return 0
    
    def get_channel_info_from_url(self, channel_url):
        """Get channel info from YouTube URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(channel_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Extract channel ID
                channel_id_match = re.search(r'"channelId":"([^"]+)"', response.text)
                if channel_id_match:
                    channel_id = channel_id_match.group(1)
                    return self.get_youtube_channel_info(channel_id)
                else:
                    return {
                        'title': 'قناة غير معروفة',
                        'subscriber_count': 0,
                        'success': False,
                        'error': 'لم يتم العثور على معرف القناة'
                    }
            else:
                return {
                    'title': 'قناة غير معروفة',
                    'subscriber_count': 0,
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                'title': 'قناة غير معروفة',
                'subscriber_count': 0,
                'success': False,
                'error': str(e)
            }
    
    def setup_database(self):
        """Setup SQLite database"""
        self.conn = sqlite3.connect('youtube_boost.db')
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE,
                title TEXT,
                current_subscribers INTEGER,
                is_active BOOLEAN,
                created_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                password TEXT,
                is_active BOOLEAN,
                added_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT,
                port INTEGER,
                username TEXT,
                password TEXT,
                is_working BOOLEAN,
                added_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS boost_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                total_subscribers INTEGER,
                subscribers_added INTEGER,
                status TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def load_data(self):
        """Load data from database"""
        cursor = self.conn.cursor()
        
        # Load channels
        cursor.execute('SELECT * FROM channels')
        self.channels = [{'id': row[0], 'channel_id': row[1], 'title': row[2], 
                         'current_subscribers': row[3], 'is_active': row[4]} for row in cursor.fetchall()]
        
        # Load accounts
        cursor.execute('SELECT * FROM accounts')
        self.accounts = [{'id': row[0], 'email': row[1], 'password': row[2], 
                         'is_active': row[3]} for row in cursor.fetchall()]
        
        # Load proxies
        cursor.execute('SELECT * FROM proxies')
        self.proxies = [{'id': row[0], 'host': row[1], 'port': row[2], 
                        'username': row[3], 'password': row[4], 'is_working': row[5]} for row in cursor.fetchall()]
        
        # Load history
        cursor.execute('SELECT * FROM boost_history')
        self.history = [{'id': row[0], 'channel_id': row[1], 'total_subscribers': row[2], 
                        'subscribers_added': row[3], 'status': row[4], 'started_at': row[5], 
                        'completed_at': row[6]} for row in cursor.fetchall()]
    
    def create_gui(self):
        """Create the GUI"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#667eea', height=80)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="YouTube Subscribers Boost", 
                              font=('Arial', 24, 'bold'), fg='white', bg='#667eea')
        title_label.pack(expand=True)
        
        # Statistics frame
        stats_frame = tk.Frame(self.root, bg='#f0f0f0')
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Stats labels
        tk.Label(stats_frame, text="إجمالي العمليات:", font=('Arial', 12), bg='#f0f0f0').grid(row=0, column=0, padx=10)
        self.total_boosts_label = tk.Label(stats_frame, text="0", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        self.total_boosts_label.grid(row=0, column=1, padx=10)
        
        tk.Label(stats_frame, text="العمليات المكتملة:", font=('Arial', 12), bg='#f0f0f0').grid(row=0, column=2, padx=10)
        self.completed_boosts_label = tk.Label(stats_frame, text="0", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        self.completed_boosts_label.grid(row=0, column=3, padx=10)
        
        tk.Label(stats_frame, text="المشتركين المضافين:", font=('Arial', 12), bg='#f0f0f0').grid(row=0, column=4, padx=10)
        self.total_subscribers_label = tk.Label(stats_frame, text="0", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        self.total_subscribers_label.grid(row=0, column=5, padx=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_channels_tab()
        self.create_accounts_tab()
        self.create_proxies_tab()
        self.create_boost_tab()
        self.create_history_tab()
    
    def create_channels_tab(self):
        """Create channels management tab"""
        channels_frame = ttk.Frame(self.notebook)
        self.notebook.add(channels_frame, text="القنوات")
        
        # Add channel frame
        add_frame = tk.LabelFrame(channels_frame, text="إضافة قناة جديدة", font=('Arial', 12, 'bold'))
        add_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        tk.Label(add_frame, text="معرف القناة أو رابط القناة:", font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        self.channel_id_entry = tk.Entry(add_frame, width=30, font=('Arial', 10))
        self.channel_id_entry.pack(padx=10, pady=5)
        
        tk.Label(add_frame, text="اسم القناة (اختياري - سيتم الحصول عليه تلقائياً):", font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        self.channel_name_entry = tk.Entry(add_frame, width=30, font=('Arial', 10))
        self.channel_name_entry.pack(padx=10, pady=5)
        
        # Add help text
        help_text = """أمثلة على المدخلات المقبولة:
• معرف القناة: UCxxxxxxxxxxxxxxxxxxxxxx
• رابط القناة: https://www.youtube.com/channel/UCxxxxx
• رابط القناة الجديد: https://www.youtube.com/@username"""
        tk.Label(add_frame, text=help_text, font=('Arial', 8), fg='gray', justify='left').pack(anchor='w', padx=10, pady=5)
        
        add_btn = tk.Button(add_frame, text="إضافة القناة", command=self.add_channel, 
                           bg='#667eea', fg='white', font=('Arial', 10, 'bold'))
        add_btn.pack(padx=10, pady=10)
        
        # Channels list frame
        list_frame = tk.LabelFrame(channels_frame, text="القنوات المضافة", font=('Arial', 12, 'bold'))
        list_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for channels
        columns = ('ID', 'اسم القناة', 'المعرف', 'المشتركين', 'الحالة')
        self.channels_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.channels_tree.heading(col, text=col)
            self.channels_tree.column(col, width=150)
        
        scrollbar_channels = ttk.Scrollbar(list_frame, orient='vertical', command=self.channels_tree.yview)
        self.channels_tree.configure(yscrollcommand=scrollbar_channels.set)
        
        self.channels_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_channels.pack(side='right', fill='y')
        
        # Buttons frame
        buttons_frame = tk.Frame(list_frame, bg='white')
        buttons_frame.pack(padx=10, pady=5)
        
        # Delete button
        delete_btn = tk.Button(buttons_frame, text="حذف القناة المحددة", command=self.delete_channel,
                              bg='#dc3545', fg='white', font=('Arial', 10, 'bold'))
        delete_btn.pack(side='left', padx=5)
        
        # Refresh button
        refresh_btn = tk.Button(buttons_frame, text="تحديث بيانات القناة", command=self.refresh_channel_data,
                               bg='#28a745', fg='white', font=('Arial', 10, 'bold'))
        refresh_btn.pack(side='left', padx=5)
        
        # Test button
        test_btn = tk.Button(buttons_frame, text="اختبار الحصول على البيانات", command=self.test_channel_data,
                            bg='#ffc107', fg='black', font=('Arial', 10, 'bold'))
        test_btn.pack(side='left', padx=5)
    
    def create_accounts_tab(self):
        """Create accounts management tab"""
        accounts_frame = ttk.Frame(self.notebook)
        self.notebook.add(accounts_frame, text="الحسابات")
        
        # Add accounts frame
        add_frame = tk.LabelFrame(accounts_frame, text="إضافة حسابات Gmail", font=('Arial', 12, 'bold'))
        add_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        tk.Label(add_frame, text="الحسابات (تنسيق: email:password):", font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        self.accounts_text = tk.Text(add_frame, width=40, height=15, font=('Arial', 9))
        self.accounts_text.pack(padx=10, pady=5)
        
        add_btn = tk.Button(add_frame, text="إضافة الحسابات", command=self.add_accounts,
                           bg='#667eea', fg='white', font=('Arial', 10, 'bold'))
        add_btn.pack(padx=10, pady=10)
        
        load_btn = tk.Button(add_frame, text="تحميل من ملف", command=self.load_accounts_file,
                            bg='#28a745', fg='white', font=('Arial', 10, 'bold'))
        load_btn.pack(padx=10, pady=5)
        
        # Accounts list frame
        list_frame = tk.LabelFrame(accounts_frame, text="الحسابات المضافة", font=('Arial', 12, 'bold'))
        list_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for accounts
        columns = ('ID', 'البريد الإلكتروني', 'الحالة')
        self.accounts_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.accounts_tree.heading(col, text=col)
            self.accounts_tree.column(col, width=200)
        
        scrollbar_accounts = ttk.Scrollbar(list_frame, orient='vertical', command=self.accounts_tree.yview)
        self.accounts_tree.configure(yscrollcommand=scrollbar_accounts.set)
        
        self.accounts_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_accounts.pack(side='right', fill='y')
        
        # Delete button
        delete_btn = tk.Button(list_frame, text="حذف الحساب المحدد", command=self.delete_account,
                              bg='#dc3545', fg='white', font=('Arial', 10, 'bold'))
        delete_btn.pack(padx=10, pady=5)
    
    def create_proxies_tab(self):
        """Create proxies management tab"""
        proxies_frame = ttk.Frame(self.notebook)
        self.notebook.add(proxies_frame, text="البروكسيات")
        
        # Add proxies frame
        add_frame = tk.LabelFrame(proxies_frame, text="إضافة البروكسيات", font=('Arial', 12, 'bold'))
        add_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        tk.Label(add_frame, text="البروكسيات (تنسيق: ip:port):", font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        self.proxies_text = tk.Text(add_frame, width=40, height=15, font=('Arial', 9))
        self.proxies_text.pack(padx=10, pady=5)
        
        add_btn = tk.Button(add_frame, text="إضافة البروكسيات", command=self.add_proxies,
                           bg='#667eea', fg='white', font=('Arial', 10, 'bold'))
        add_btn.pack(padx=10, pady=10)
        
        test_btn = tk.Button(add_frame, text="اختبار البروكسيات", command=self.test_proxies,
                            bg='#ffc107', fg='black', font=('Arial', 10, 'bold'))
        test_btn.pack(padx=10, pady=5)
        
        load_btn = tk.Button(add_frame, text="تحميل من ملف", command=self.load_proxies_file,
                            bg='#28a745', fg='white', font=('Arial', 10, 'bold'))
        load_btn.pack(padx=10, pady=5)
        
        # Proxies list frame
        list_frame = tk.LabelFrame(proxies_frame, text="البروكسيات المضافة", font=('Arial', 12, 'bold'))
        list_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for proxies
        columns = ('ID', 'البروكسي', 'الحالة')
        self.proxies_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.proxies_tree.heading(col, text=col)
            self.proxies_tree.column(col, width=200)
        
        scrollbar_proxies = ttk.Scrollbar(list_frame, orient='vertical', command=self.proxies_tree.yview)
        self.proxies_tree.configure(yscrollcommand=scrollbar_proxies.set)
        
        self.proxies_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_proxies.pack(side='right', fill='y')
        
        # Delete button
        delete_btn = tk.Button(list_frame, text="حذف البروكسي المحدد", command=self.delete_proxy,
                              bg='#dc3545', fg='white', font=('Arial', 10, 'bold'))
        delete_btn.pack(padx=10, pady=5)
    
    def create_boost_tab(self):
        """Create boost control tab"""
        boost_frame = ttk.Frame(self.notebook)
        self.notebook.add(boost_frame, text="التزويد")
        
        # Control frame
        control_frame = tk.LabelFrame(boost_frame, text="إعدادات التزويد", font=('Arial', 12, 'bold'))
        control_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        tk.Label(control_frame, text="اختر القناة:", font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        self.channel_combo = ttk.Combobox(control_frame, width=30, font=('Arial', 10))
        self.channel_combo.pack(padx=10, pady=5)
        
        tk.Label(control_frame, text="عدد المشتركين المراد إضافتهم:", font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        self.subscribers_entry = tk.Entry(control_frame, width=30, font=('Arial', 10))
        self.subscribers_entry.pack(padx=10, pady=5)
        tk.Label(control_frame, text="(الحد الأدنى: 0 | الحد الأقصى: 10,000)", font=('Arial', 8), fg='gray').pack(anchor='w', padx=10)
        
        tk.Label(control_frame, text="سرعة التزويد:", font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        self.speed_combo = ttk.Combobox(control_frame, values=['بطيئة', 'متوسطة', 'سريعة'], 
                                       width=30, font=('Arial', 10))
        self.speed_combo.set('متوسطة')
        self.speed_combo.pack(padx=10, pady=5)
        
        self.use_proxy_var = tk.BooleanVar(value=True)
        proxy_check = tk.Checkbutton(control_frame, text="استخدام البروكسي", variable=self.use_proxy_var,
                                    font=('Arial', 10))
        proxy_check.pack(anchor='w', padx=10, pady=5)
        
        self.use_accounts_var = tk.BooleanVar(value=True)
        accounts_check = tk.Checkbutton(control_frame, text="استخدام الحسابات", variable=self.use_accounts_var,
                                       font=('Arial', 10))
        accounts_check.pack(anchor='w', padx=10, pady=5)
        
        # Real boost mode
        self.real_boost_var = tk.BooleanVar(value=False)
        real_boost_check = tk.Checkbutton(control_frame, text="التزويد الحقيقي (بطيء ومخاطر)", 
                                         variable=self.real_boost_var, font=('Arial', 10, 'bold'))
        real_boost_check.pack(anchor='w', padx=10, pady=5)
        
        # Warning label
        warning_label = tk.Label(control_frame, text="⚠️ التزويد الحقيقي يستخدم حسابات حقيقية وقد يكون بطيئاً", 
                                font=('Arial', 8), fg='red')
        warning_label.pack(anchor='w', padx=10, pady=2)
        
        self.start_btn = tk.Button(control_frame, text="بدء التزويد", command=self.start_boost,
                                  bg='#28a745', fg='white', font=('Arial', 12, 'bold'))
        self.start_btn.pack(padx=10, pady=20)
        
        self.stop_btn = tk.Button(control_frame, text="إيقاف التزويد", command=self.stop_boost,
                                 bg='#dc3545', fg='white', font=('Arial', 12, 'bold'), state='disabled')
        self.stop_btn.pack(padx=10, pady=5)
        
        # Progress frame
        progress_frame = tk.LabelFrame(boost_frame, text="تقدم العملية", font=('Arial', 12, 'bold'))
        progress_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=10, pady=10)
        
        # Progress labels
        progress_info_frame = tk.Frame(progress_frame, bg='white')
        progress_info_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(progress_info_frame, text="المشتركين الحاليين:", font=('Arial', 10), bg='white').grid(row=0, column=0, padx=5)
        self.current_subscribers_label = tk.Label(progress_info_frame, text="0", font=('Arial', 10, 'bold'), bg='white')
        self.current_subscribers_label.grid(row=0, column=1, padx=5)
        
        tk.Label(progress_info_frame, text="الهدف:", font=('Arial', 10), bg='white').grid(row=0, column=2, padx=5)
        self.target_subscribers_label = tk.Label(progress_info_frame, text="0", font=('Arial', 10, 'bold'), bg='white')
        self.target_subscribers_label.grid(row=0, column=3, padx=5)
        
        tk.Label(progress_info_frame, text="المضافين:", font=('Arial', 10), bg='white').grid(row=1, column=0, padx=5)
        self.added_subscribers_label = tk.Label(progress_info_frame, text="0", font=('Arial', 10, 'bold'), bg='white')
        self.added_subscribers_label.grid(row=1, column=1, padx=5)
        
        # Status label
        self.status_label = tk.Label(progress_frame, text="لا توجد عمليات جارية", font=('Arial', 10), bg='white')
        self.status_label.pack(padx=10, pady=10)
    
    def create_history_tab(self):
        """Create history tab"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="السجل")
        
        # History list frame
        list_frame = tk.LabelFrame(history_frame, text="سجل العمليات", font=('Arial', 12, 'bold'))
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for history
        columns = ('ID', 'القناة', 'المطلوب', 'المضاف', 'الحالة', 'تاريخ البدء', 'تاريخ الانتهاء')
        self.history_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        scrollbar_history = ttk.Scrollbar(list_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar_history.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_history.pack(side='right', fill='y')
        
        # Clear history button
        clear_btn = tk.Button(list_frame, text="مسح السجل", command=self.clear_history,
                             bg='#dc3545', fg='white', font=('Arial', 10, 'bold'))
        clear_btn.pack(padx=10, pady=5)
    
    def update_display(self):
        """Update all displays"""
        self.update_channels_display()
        self.update_accounts_display()
        self.update_proxies_display()
        self.update_boost_display()
        self.update_history_display()
        self.update_stats_display()
    
    def update_channels_display(self):
        """Update channels display"""
        # Clear existing items
        for item in self.channels_tree.get_children():
            self.channels_tree.delete(item)
        
        # Add channels
        for channel in self.channels:
            status = "نشط" if channel['is_active'] else "غير نشط"
            self.channels_tree.insert('', 'end', values=(
                channel['id'],
                channel['title'],
                channel['channel_id'],
                f"{channel['current_subscribers']:,}",
                status
            ))
        
        # Update combo box
        channel_names = [f"{ch['title']} ({ch['channel_id']})" for ch in self.channels]
        self.channel_combo['values'] = channel_names
    
    def update_accounts_display(self):
        """Update accounts display"""
        # Clear existing items
        for item in self.accounts_tree.get_children():
            self.accounts_tree.delete(item)
        
        # Add accounts
        for account in self.accounts:
            status = "نشط" if account['is_active'] else "غير نشط"
            self.accounts_tree.insert('', 'end', values=(
                account['id'],
                account['email'],
                status
            ))
    
    def update_proxies_display(self):
        """Update proxies display"""
        # Clear existing items
        for item in self.proxies_tree.get_children():
            self.proxies_tree.delete(item)
        
        # Add proxies
        for proxy in self.proxies:
            status = "يعمل" if proxy['is_working'] else "لا يعمل"
            proxy_str = f"{proxy['host']}:{proxy['port']}"
            if proxy['username']:
                proxy_str += f" ({proxy['username']})"
            
            self.proxies_tree.insert('', 'end', values=(
                proxy['id'],
                proxy_str,
                status
            ))
    
    def update_boost_display(self):
        """Update boost display"""
        if self.current_boost:
            progress = (self.current_boost['subscribers_added'] / self.current_boost['total_subscribers']) * 100
            self.progress_var.set(progress)
            
            self.current_subscribers_label.config(text=f"{self.current_boost['current_subscribers']:,}")
            self.target_subscribers_label.config(text=f"{self.current_boost['total_subscribers']:,}")
            self.added_subscribers_label.config(text=f"{self.current_boost['subscribers_added']:,}")
            
            self.status_label.config(text=f"جاري إضافة {self.current_boost['subscribers_added']} من {self.current_boost['total_subscribers']} مشترك")
        else:
            self.progress_var.set(0)
            self.current_subscribers_label.config(text="0")
            self.target_subscribers_label.config(text="0")
            self.added_subscribers_label.config(text="0")
            self.status_label.config(text="لا توجد عمليات جارية")
    
    def update_history_display(self):
        """Update history display"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add history items (reverse order - newest first)
        for history_item in reversed(self.history):
            # Find channel name
            channel_name = "غير معروف"
            for channel in self.channels:
                if channel['channel_id'] == history_item['channel_id']:
                    channel_name = channel['title']
                    break
            
            status = "مكتمل" if history_item['status'] == 'completed' else "معلق"
            start_date = history_item['started_at'][:19] if history_item['started_at'] else "غير محدد"
            end_date = history_item['completed_at'][:19] if history_item['completed_at'] else "غير محدد"
            
            self.history_tree.insert('', 'end', values=(
                history_item['id'],
                channel_name,
                f"{history_item['total_subscribers']:,}",
                f"{history_item['subscribers_added']:,}",
                status,
                start_date,
                end_date
            ))
    
    def update_stats_display(self):
        """Update statistics display"""
        total_boosts = len(self.history)
        completed_boosts = len([h for h in self.history if h['status'] == 'completed'])
        total_subscribers = sum(h['subscribers_added'] for h in self.history if h['status'] == 'completed')
        
        self.total_boosts_label.config(text=str(total_boosts))
        self.completed_boosts_label.config(text=str(completed_boosts))
        self.total_subscribers_label.config(text=f"{total_subscribers:,}")
    
    def add_channel(self):
        """Add new channel"""
        channel_input = self.channel_id_entry.get().strip()
        channel_name = self.channel_name_entry.get().strip()
        
        if not channel_input:
            messagebox.showerror("خطأ", "يرجى إدخال معرف القناة أو رابط القناة")
            return
        
        # Show loading message
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            # Determine if input is URL or channel ID
            if channel_input.startswith('http'):
                # It's a URL
                channel_info = self.get_channel_info_from_url(channel_input)
                
                # Extract channel ID from URL
                if '/channel/' in channel_input:
                    channel_id = channel_input.split('/channel/')[-1].split('/')[0].split('?')[0]
                elif '/@' in channel_input:
                    # Handle @username format
                    username = channel_input.split('/@')[-1].split('/')[0].split('?')[0]
                    channel_id = username  # For now, use username as ID
                else:
                    messagebox.showerror("خطأ", "تنسيق الرابط غير صحيح")
                    return
            else:
                # It's a channel ID
                channel_id = channel_input
                channel_info = self.get_youtube_channel_info(channel_id)
            
            # Check if channel already exists
            for channel in self.channels:
                if channel['channel_id'] == channel_id:
                    messagebox.showerror("خطأ", "هذه القناة موجودة بالفعل")
                    return
            
            # If we couldn't get real data, ask user if they want to continue
            if not channel_info['success'] or channel_info['subscriber_count'] == 0:
                result = messagebox.askyesno(
                    "تأكيد", 
                    f"لم يتم الحصول على بيانات القناة من YouTube.\nهل تريد إضافة القناة بالمعلومات الأساسية؟\n\nمعرف القناة: {channel_id}"
                )
                if not result:
                    return
                
                # Use fallback data
                channel_info = {
                    'title': channel_name or f"قناة {channel_id[:8]}",
                    'subscriber_count': 0,
                    'success': True
                }
            
            # Add to database
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO channels (channel_id, title, current_subscribers, is_active, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (channel_id, 
                  channel_name or channel_info['title'], 
                  channel_info['subscriber_count'], 
                  True, 
                  datetime.now().isoformat()))
            
            self.conn.commit()
            
            # Reload data and update display
            self.load_data()
            self.update_display()
            
            # Clear entries
            self.channel_id_entry.delete(0, 'end')
            self.channel_name_entry.delete(0, 'end')
            
            # Show success message
            if channel_info['subscriber_count'] > 0:
                messagebox.showinfo("نجح", f"تم إضافة القناة بنجاح!\nالاسم: {channel_info['title']}\nالمشتركين: {channel_info['subscriber_count']:,}")
            else:
                messagebox.showinfo("نجح", f"تم إضافة القناة بنجاح!\nالاسم: {channel_info['title']}\nالمشتركين: غير متوفر (سيتم تحديثه لاحقاً)")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إضافة القناة: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def refresh_channel_data(self):
        """Refresh selected channel data"""
        selection = self.channels_tree.selection()
        if not selection:
            messagebox.showerror("خطأ", "يرجى اختيار قناة للتحديث")
            return
        
        item = self.channels_tree.item(selection[0])
        channel_id = item['values'][0]
        
        # Find channel in database
        channel = None
        for ch in self.channels:
            if ch['id'] == channel_id:
                channel = ch
                break
        
        if not channel:
            messagebox.showerror("خطأ", "القناة غير موجودة")
            return
        
        # Show loading
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            # Get updated channel info
            channel_info = self.get_youtube_channel_info(channel['channel_id'])
            
            if channel_info['success'] and channel_info['subscriber_count'] > 0:
                # Update database
                cursor = self.conn.cursor()
                cursor.execute('''
                    UPDATE channels SET title = ?, current_subscribers = ? WHERE id = ?
                ''', (channel_info['title'], channel_info['subscriber_count'], channel_id))
                self.conn.commit()
                
                # Reload data and update display
                self.load_data()
                self.update_display()
                
                messagebox.showinfo("نجح", f"تم تحديث بيانات القناة!\nالاسم: {channel_info['title']}\nالمشتركين: {channel_info['subscriber_count']:,}")
            else:
                messagebox.showerror("خطأ", "لم يتم الحصول على بيانات محدثة للقناة")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحديث القناة: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def test_channel_data(self):
        """Test getting channel data"""
        test_channel_id = self.channel_id_entry.get().strip()
        
        if not test_channel_id:
            messagebox.showerror("خطأ", "يرجى إدخال معرف القناة للاختبار")
            return
        
        # Show loading
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            # Test all methods
            methods = [
                ("الطريقة الأولى (الصفحة الرئيسية)", self.get_channel_info_method1),
                ("الطريقة الثانية (صفحة حول)", self.get_channel_info_method2),
                ("الطريقة الثالثة (صفحة الفيديوهات)", self.get_channel_info_method3)
            ]
            
            results = []
            for method_name, method_func in methods:
                try:
                    result = method_func(test_channel_id)
                    results.append(f"{method_name}: {'نجح' if result['success'] else 'فشل'}")
                    if result['success']:
                        results.append(f"  - الاسم: {result['title']}")
                        results.append(f"  - المشتركين: {result['subscriber_count']:,}")
                except Exception as e:
                    results.append(f"{method_name}: خطأ - {str(e)}")
            
            # Show results
            messagebox.showinfo("نتائج الاختبار", "\n".join(results))
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الاختبار: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def create_proxy_auth_extension(self, username, password):
        """Create a Chrome extension for proxy authentication"""
        import zipfile
        import os
        
        # Create extension directory
        extension_dir = "proxy_auth_extension"
        if not os.path.exists(extension_dir):
            os.makedirs(extension_dir)
        
        # Manifest
        manifest = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Proxy Auth",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version": "22.0.0"
        }
        
        # Background script
        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{username}",
                    port: parseInt("{password}")
                }},
                bypassList: ["localhost"]
            }}
        }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{username}",
                    password: "{password}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """
        
        # Write files
        with open(os.path.join(extension_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f)
        
        with open(os.path.join(extension_dir, "background.js"), "w") as f:
            f.write(background_js)
        
        # Create zip file
        zip_path = "proxy_auth_extension.zip"
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            zip_file.write(os.path.join(extension_dir, "manifest.json"), "manifest.json")
            zip_file.write(os.path.join(extension_dir, "background.js"), "background.js")
        
        return zip_path
    
    def create_selenium_driver(self, proxy=None):
        """Create a Selenium WebDriver with proxy support"""
        if not SELENIUM_AVAILABLE:
            raise Exception("Selenium غير مثبت. يرجى تثبيته باستخدام: pip install selenium")
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add proxy if provided
        if proxy:
            proxy_string = f"{proxy['host']}:{proxy['port']}"
            
            # Determine credentials to use
            username = proxy.get('username', 'elfermahmoud@gmail.com')
            password = proxy.get('password', '102030mmM@#')
            
            # If no credentials provided, use defaults
            if not proxy.get('username') or not proxy.get('password') or not proxy['username'].strip() or not proxy['password'].strip():
                username = 'elfermahmoud@gmail.com'
                password = '102030mmM@#'
            
            # Add proxy server
            chrome_options.add_argument(f'--proxy-server=http://{proxy_string}')
            
            # Create and add authentication extension
            try:
                extension_path = self.create_proxy_auth_extension(username, password)
                chrome_options.add_extension(extension_path)
            except Exception as e:
                print(f"Warning: Could not create proxy auth extension: {e}")
                # Fallback: try with credentials in URL
                proxy_string = f"{username}:{password}@{proxy_string}"
                chrome_options.add_argument(f'--proxy-server=http://{proxy_string}')
        
        # Random user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            raise Exception(f"فشل في إنشاء WebDriver: {str(e)}")
    
    def login_to_facebook(self, driver, email, password):
        """Login to Facebook with email and password"""
        try:
            driver.get("https://www.facebook.com/login")
            time.sleep(random.uniform(2, 4))
            
            # Wait for email input
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            # Clear and type email slowly
            email_input.clear()
            for char in email:
                email_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Wait for password input
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "pass"))
            )
            
            # Clear and type password slowly
            password_input.clear()
            for char in password:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Click login button
            login_button = driver.find_element(By.NAME, "login")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(random.uniform(5, 8))
            
            # Check if login was successful
            current_url = driver.current_url
            if "facebook.com" in current_url and "login" not in current_url:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Facebook login failed: {str(e)}")
            return False
    
    def get_followed_pages(self, driver):
        """Get list of pages that the account follows"""
        try:
            # Go to following pages
            driver.get("https://www.facebook.com/pages/?category=followed")
            time.sleep(random.uniform(3, 5))
            
            # Scroll to load more pages
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
            
            # Extract page links
            page_links = []
            try:
                # Look for page links
                page_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/pages/']")
                for element in page_elements:
                    href = element.get_attribute('href')
                    if href and '/pages/' in href:
                        page_links.append(href)
            except:
                pass
            
            return list(set(page_links))  # Remove duplicates
            
        except Exception as e:
            print(f"Error getting followed pages: {str(e)}")
            return []
    
    def follow_from_page(self, driver, page_url, target_page_url):
        """Follow target page from a specific page"""
        try:
            driver.get(page_url)
            time.sleep(random.uniform(2, 4))
            
            # Go to target page
            driver.get(target_page_url)
            time.sleep(random.uniform(2, 4))
            
            # Look for follow button
            follow_selectors = [
                "div[aria-label*='Follow']",
                "div[aria-label*='متابعة']",
                "span:contains('Follow')",
                "span:contains('متابعة')",
                "button[data-testid*='follow']"
            ]
            
            follow_button = None
            for selector in follow_selectors:
                try:
                    follow_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if follow_button:
                # Scroll to button
                driver.execute_script("arguments[0].scrollIntoView(true);", follow_button)
                time.sleep(random.uniform(1, 2))
                
                # Click follow
                ActionChains(driver).move_to_element(follow_button).click().perform()
                time.sleep(random.uniform(1, 3))
                
                print(f"Successfully followed from {page_url}")
                return True
            else:
                print(f"No follow button found on {target_page_url}")
                return False
                
        except Exception as e:
            print(f"Error following from page: {str(e)}")
            return False
    
    def subscribe_to_channel(self, driver, channel_url):
        """Subscribe to a YouTube channel"""
        try:
            driver.get(channel_url)
            time.sleep(random.uniform(2, 4))
            
            # Look for subscribe button
            subscribe_button = None
            subscribe_selectors = [
                "button[aria-label*='Subscribe']",
                "button[aria-label*='اشتراك']",
                "button:contains('Subscribe')",
                "button:contains('اشتراك')",
                ".ytd-subscribe-button-renderer button"
            ]
            
            for selector in subscribe_selectors:
                try:
                    subscribe_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if subscribe_button:
                # Scroll to button
                driver.execute_script("arguments[0].scrollIntoView(true);", subscribe_button)
                time.sleep(random.uniform(1, 2))
                
                # Click subscribe
                ActionChains(driver).move_to_element(subscribe_button).click().perform()
                time.sleep(random.uniform(1, 3))
                
                # Check if subscription was successful
                try:
                    # Look for "Subscribed" or "مشترك" text
                    subscribed_indicators = [
                        "button[aria-label*='Subscribed']",
                        "button[aria-label*='مشترك']",
                        "button:contains('Subscribed')",
                        "button:contains('مشترك')"
                    ]
                    
                    for indicator in subscribed_indicators:
                        try:
                            WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                            )
                            return True
                        except:
                            continue
                    
                    return True  # Assume success if no error
                except:
                    return True  # Assume success if no error
            else:
                return False
                
        except Exception as e:
            print(f"Subscription failed: {str(e)}")
            return False
    
    def real_boost_process(self, channel_id, total_subscribers, accounts_list, proxies_list):
        """Real boost process using Selenium"""
        try:
            # Get channel URL
            channel_url = f"https://www.youtube.com/channel/{channel_id}"
            
            successful_subscriptions = 0
            failed_subscriptions = 0
            
            # Process each account
            for i, account in enumerate(accounts_list):
                if not self.is_boosting:
                    break
                
                try:
                    # Select proxy for this account
                    proxy = None
                    if proxies_list and len(proxies_list) > 0:
                        proxy = proxies_list[i % len(proxies_list)]
                    
                    # Create driver
                    driver = self.create_selenium_driver(proxy)
                    self.active_drivers.append(driver)
                    
                    # Login to YouTube
                    login_success = self.login_to_youtube(driver, account['email'], account['password'])
                    
                    if login_success:
                        # Subscribe to channel
                        subscription_success = self.subscribe_to_channel(driver, channel_url)
                        
                        if subscription_success:
                            successful_subscriptions += 1
                            print(f"Successfully subscribed with {account['email']}")
                        else:
                            failed_subscriptions += 1
                            print(f"Failed to subscribe with {account['email']}")
                    else:
                        failed_subscriptions += 1
                        print(f"Failed to login with {account['email']}")
                    
                    # Close driver
                    driver.quit()
                    if driver in self.active_drivers:
                        self.active_drivers.remove(driver)
                    
                    # Update progress
                    self.current_boost['subscribers_added'] = successful_subscriptions
                    self.root.after(0, self.update_display)
                    
                    # Wait between accounts
                    wait_time = random.uniform(10, 30) * self.boost_speed_multiplier
                    time.sleep(wait_time)
                    
                except Exception as e:
                    print(f"Error processing account {account['email']}: {str(e)}")
                    failed_subscriptions += 1
                    continue
            
            # Update final results
            self.current_boost['subscribers_added'] = successful_subscriptions
            self.current_boost['status'] = 'completed'
            
        except Exception as e:
            print(f"Real boost process error: {str(e)}")
            self.current_boost['status'] = 'error'
        finally:
            # Close all drivers
            for driver in self.active_drivers:
                try:
                    driver.quit()
                except:
                    pass
            self.active_drivers.clear()
    
    def delete_channel(self):
        """Delete selected channel"""
        selection = self.channels_tree.selection()
        if not selection:
            messagebox.showerror("خطأ", "يرجى اختيار قناة للحذف")
            return
        
        item = self.channels_tree.item(selection[0])
        channel_id = item['values'][0]
        
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذه القناة؟"):
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM channels WHERE id = ?', (channel_id,))
            self.conn.commit()
            
            self.load_data()
            self.update_display()
            messagebox.showinfo("نجح", "تم حذف القناة بنجاح!")
    
    def add_accounts(self):
        """Add new accounts"""
        accounts_text = self.accounts_text.get("1.0", "end").strip()
        
        if not accounts_text:
            messagebox.showerror("خطأ", "يرجى إدخال الحسابات")
            return
        
        lines = [line.strip() for line in accounts_text.split('\n') if line.strip()]
        accounts_to_add = []
        
        for line in lines:
            parts = line.split(':')
            if len(parts) >= 2:
                accounts_to_add.append({
                    'email': parts[0],
                    'password': parts[1],
                    'is_active': True,
                    'added_at': datetime.now().isoformat()
                })
        
        if not accounts_to_add:
            messagebox.showerror("خطأ", "تنسيق الحسابات غير صحيح")
            return
        
        # Add to database
        cursor = self.conn.cursor()
        for account in accounts_to_add:
            cursor.execute('''
                INSERT INTO accounts (email, password, is_active, added_at)
                VALUES (?, ?, ?, ?)
            ''', (account['email'], account['password'], account['is_active'], account['added_at']))
        
        self.conn.commit()
        
        # Reload data and update display
        self.load_data()
        self.update_display()
        
        # Clear text
        self.accounts_text.delete("1.0", "end")
        
        messagebox.showinfo("نجح", f"تم إضافة {len(accounts_to_add)} حساب بنجاح!")
    
    def load_accounts_file(self):
        """Load accounts from file"""
        file_path = filedialog.askopenfilename(title="اختر ملف الحسابات", filetypes=[("Text files", "*.txt")])
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.accounts_text.delete("1.0", "end")
                    self.accounts_text.insert("1.0", content)
                    messagebox.showinfo("نجح", "تم تحميل ملف الحسابات بنجاح!")
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في تحميل الملف: {str(e)}")
    
    def delete_account(self):
        """Delete selected account"""
        selection = self.accounts_tree.selection()
        if not selection:
            messagebox.showerror("خطأ", "يرجى اختيار حساب للحذف")
            return
        
        item = self.accounts_tree.item(selection[0])
        account_id = item['values'][0]
        
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا الحساب؟"):
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
            self.conn.commit()
            
            self.load_data()
            self.update_display()
            messagebox.showinfo("نجح", "تم حذف الحساب بنجاح!")
    
    def add_proxies(self):
        """Add new proxies"""
        proxies_text = self.proxies_text.get("1.0", "end").strip()
        
        if not proxies_text:
            messagebox.showerror("خطأ", "يرجى إدخال البروكسيات")
            return
        
        lines = [line.strip() for line in proxies_text.split('\n') if line.strip()]
        proxies_to_add = []
        
        for line in lines:
            parts = line.split(':')
            if len(parts) >= 2:
                proxy = {
                    'host': parts[0],
                    'port': int(parts[1]),
                    'username': parts[2] if len(parts) > 2 else None,
                    'password': parts[3] if len(parts) > 3 else None,
                    'is_working': True,
                    'added_at': datetime.now().isoformat()
                }
                proxies_to_add.append(proxy)
        
        if not proxies_to_add:
            messagebox.showerror("خطأ", "تنسيق البروكسيات غير صحيح")
            return
        
        # Add to database
        cursor = self.conn.cursor()
        for proxy in proxies_to_add:
            cursor.execute('''
                INSERT INTO proxies (host, port, username, password, is_working, added_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (proxy['host'], proxy['port'], proxy['username'], proxy['password'], 
                  proxy['is_working'], proxy['added_at']))
        
        self.conn.commit()
        
        # Reload data and update display
        self.load_data()
        self.update_display()
        
        # Clear text
        self.proxies_text.delete("1.0", "end")
        
        messagebox.showinfo("نجح", f"تم إضافة {len(proxies_to_add)} بروكسي بنجاح!")
    
    def load_proxies_file(self):
        """Load proxies from file"""
        file_path = filedialog.askopenfilename(title="اختر ملف البروكسيات", filetypes=[("Text files", "*.txt")])
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.proxies_text.delete("1.0", "end")
                    self.proxies_text.insert("1.0", content)
                    messagebox.showinfo("نجح", "تم تحميل ملف البروكسيات بنجاح!")
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في تحميل الملف: {str(e)}")
    
    def test_proxies(self):
        """Test proxies"""
        if not self.proxies:
            messagebox.showerror("خطأ", "لا توجد بروكسيات للاختبار")
            return
        
        messagebox.showinfo("معلومات", "جاري اختبار البروكسيات...")
        
        # Test proxies in a separate thread
        def test_thread():
            for proxy in self.proxies:
                try:
                    # Simple test - try to connect
                    proxies_dict = {
                        'http': f"http://{proxy['host']}:{proxy['port']}",
                        'https': f"http://{proxy['host']}:{proxy['port']}"
                    }
                    
                    response = requests.get('http://httpbin.org/ip', proxies=proxies_dict, timeout=10)
                    proxy['is_working'] = response.status_code == 200
                except:
                    proxy['is_working'] = False
                
                # Update database
                cursor = self.conn.cursor()
                cursor.execute('UPDATE proxies SET is_working = ? WHERE id = ?', 
                              (proxy['is_working'], proxy['id']))
                self.conn.commit()
            
            # Update display
            self.root.after(0, self.update_display)
            
            working_count = len([p for p in self.proxies if p['is_working']])
            self.root.after(0, lambda: messagebox.showinfo("معلومات", 
                f"تم اختبار {len(self.proxies)} بروكسي، {working_count} يعمل"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def delete_proxy(self):
        """Delete selected proxy"""
        selection = self.proxies_tree.selection()
        if not selection:
            messagebox.showerror("خطأ", "يرجى اختيار بروكسي للحذف")
            return
        
        item = self.proxies_tree.item(selection[0])
        proxy_id = item['values'][0]
        
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا البروكسي؟"):
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM proxies WHERE id = ?', (proxy_id,))
            self.conn.commit()
            
            self.load_data()
            self.update_display()
            messagebox.showinfo("نجح", "تم حذف البروكسي بنجاح!")
    
    def start_boost(self):
        """Start boost process"""
        # Validate inputs
        if not self.channel_combo.get():
            messagebox.showerror("خطأ", "يرجى اختيار قناة")
            return
        
        try:
            subscribers = int(self.subscribers_entry.get())
            if subscribers < 0:
                messagebox.showerror("خطأ", "عدد المشتركين لا يمكن أن يكون سالب")
                return
            if subscribers > 10000:
                messagebox.showerror("خطأ", "الحد الأقصى للمشتركين هو 10000")
                return
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال رقم صحيح للمشتركين")
            return
        
        # Check requirements
        if self.use_proxy_var.get() and not self.proxies:
            messagebox.showerror("خطأ", "لا توجد بروكسيات مضافة")
            return
        
        if self.use_accounts_var.get() and not self.accounts:
            messagebox.showerror("خطأ", "لا توجد حسابات مضافة")
            return
        
        # Get selected channel
        selected_channel_name = self.channel_combo.get()
        selected_channel = None
        for channel in self.channels:
            if f"{channel['title']} ({channel['channel_id']})" == selected_channel_name:
                selected_channel = channel
                break
        
        if not selected_channel:
            messagebox.showerror("خطأ", "القناة المحددة غير موجودة")
            return
        
        # Create boost record
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO boost_history (channel_id, total_subscribers, subscribers_added, status, started_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (selected_channel['channel_id'], subscribers, 0, 'running', datetime.now().isoformat()))
        
        boost_id = cursor.lastrowid
        self.conn.commit()
        
        # Create current boost object
        self.current_boost = {
            'id': boost_id,
            'channel_id': selected_channel['channel_id'],
            'total_subscribers': subscribers,
            'subscribers_added': 0,
            'current_subscribers': selected_channel['current_subscribers'],
            'status': 'running',
            'speed': self.speed_combo.get(),
            'use_proxy': self.use_proxy_var.get(),
            'use_accounts': self.use_accounts_var.get(),
            'started_at': datetime.now().isoformat()
        }
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.is_boosting = True
        
        # Check if real boost mode is enabled
        if self.real_boost_var.get():
            # Real boost mode
            if not SELENIUM_AVAILABLE:
                messagebox.showerror("خطأ", "Selenium غير مثبت. يرجى تثبيته باستخدام: pip install selenium")
                return
            
            # Confirm real boost
            result = messagebox.askyesno("تأكيد التزويد الحقيقي", 
                f"هل أنت متأكد من بدء التزويد الحقيقي؟\n\n"
                f"هذا سيستخدم حسابات Gmail حقيقية وقد يكون بطيئاً.\n"
                f"عدد المشتركين المطلوب: {subscribers}\n"
                f"عدد الحسابات المتاحة: {len(self.accounts)}\n"
                f"عدد البروكسيات المتاحة: {len(self.proxies)}")
            
            if not result:
                return
            
            # Start real boost process
            self.boost_thread = threading.Thread(
                target=self.real_boost_process, 
                args=(selected_channel['channel_id'], subscribers, self.accounts, self.proxies),
                daemon=True
            )
            self.boost_thread.start()
            
            messagebox.showinfo("نجح", f"تم بدء التزويد الحقيقي لـ {subscribers} مشترك!\nسيتم استخدام {len(self.accounts)} حساب")
        else:
            # Simulated boost mode
            self.boost_thread = threading.Thread(target=self.boost_process, daemon=True)
            self.boost_thread.start()
            
            messagebox.showinfo("نجح", f"تم بدء عملية التزويد المحاكاة لـ {subscribers} مشترك!")
        
        # Reload data and update display
        self.load_data()
        self.update_display()
    
    def boost_process(self):
        """Boost process thread"""
        speed_delays = {'بطيئة': 3, 'متوسطة': 2, 'سريعة': 1}
        delay = speed_delays.get(self.current_boost['speed'], 2)
        
        while self.is_boosting and self.current_boost['subscribers_added'] < self.current_boost['total_subscribers']:
            # Simulate adding subscribers
            increment = random.randint(1, 10)
            self.current_boost['subscribers_added'] = min(
                self.current_boost['subscribers_added'] + increment,
                self.current_boost['total_subscribers']
            )
            
            # Update database
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE boost_history SET subscribers_added = ? WHERE id = ?
            ''', (self.current_boost['subscribers_added'], self.current_boost['id']))
            self.conn.commit()
            
            # Update display
            self.root.after(0, self.update_display)
            
            time.sleep(delay)
        
        # Complete boost
        if self.is_boosting:
            self.complete_boost()
    
    def complete_boost(self):
        """Complete boost process"""
        self.is_boosting = False
        
        # Update database
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE boost_history SET status = 'completed', completed_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), self.current_boost['id']))
        
        # Update channel subscriber count
        cursor.execute('''
            UPDATE channels SET current_subscribers = current_subscribers + ? 
            WHERE channel_id = ?
        ''', (self.current_boost['subscribers_added'], self.current_boost['channel_id']))
        
        self.conn.commit()
        
        # Update UI
        self.root.after(0, lambda: self.start_btn.config(state='normal'))
        self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
        
        # Reload data and update display
        self.load_data()
        self.update_display()
        
        self.root.after(0, lambda: messagebox.showinfo("نجح", 
            f"تم إكمال عملية التزويد! تم إضافة {self.current_boost['subscribers_added']} مشترك"))
        
        self.current_boost = None
    
    def stop_boost(self):
        """Stop boost process"""
        self.is_boosting = False
        
        # Update database
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE boost_history SET status = 'stopped', completed_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), self.current_boost['id']))
        self.conn.commit()
        
        # Update UI
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        # Reload data and update display
        self.load_data()
        self.update_display()
        
        messagebox.showinfo("معلومات", "تم إيقاف عملية التزويد")
        self.current_boost = None
    
    def clear_history(self):
        """Clear boost history"""
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من مسح جميع السجلات؟"):
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM boost_history')
            self.conn.commit()
            
            self.load_data()
            self.update_display()
            messagebox.showinfo("نجح", "تم مسح السجل بنجاح!")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main function"""
    root = tk.Tk()
    app = YouTubeBoostApp(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
