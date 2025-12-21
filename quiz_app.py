import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Master Admin", 
    page_icon="meshack.png", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. Base64 Image
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_raw = get_base64_image("meshack.png")
img_data = f"data:image/png;base64,{img_raw}" if img_raw else ""

# 3. PWA & Icon Injection
manifest_json = f"""
{{
    "name": "Master Admin System",
    "short_name": "MasterAdmin",
    "icons": [
        {{ "src": "{img_data}", "sizes": "192x192", "type": "image/png" }},
        {{ "src": "{img_data}", "sizes": "512x512", "type": "image/png" }}
    ],
    "start_url": ".",
    "display": "standalone",
    "theme_color": "#15803d",
    "background_color": "#061a06"
}}
"""
manifest_b64 = base64.b64encode(manifest_json.encode()).decode()

st.markdown(f"""
    <script>
        var link = document.querySelector("link[rel*='icon']") || document.createElement('link');
        link.type = 'image/png'; link.rel = 'shortcut icon'; link.href = '{img_data}';
        document.getElementsByTagName('head')[0].appendChild(link);
        var manifestLink = document.createElement('link');
        manifestLink.rel = 'manifest'; manifestLink.href = 'data:application/manifest+json;base64,{manifest_b64}';
        document.getElementsByTagName('head')[0].appendChild(manifestLink);
    </script>
    <style>
        #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
        .block-container {{padding: 0px !important;}} iframe {{border: none !important;}}
    </style>
""", unsafe_allow_html=True)

# 4. FULL SYSTEM CODE WITH REALTIME NOTIFICATIONS
full_custom_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f0f4f0; margin: 0; }}
        [x-cloak] {{ display: none !important; }}
        .notification-toast {{
            position: fixed; top: 20px; right: 20px; z-index: 100;
            animation: slideIn 0.5s ease-out forwards;
        }}
        @keyframes slideIn {{ from {{ transform: translateX(100%); opacity: 0; }} to {{ transform: translateX(0); opacity: 1; }} }}
        .gradient-green {{ background: linear-gradient(135deg, #15803d 0%, #166534 100%); }}
    </style>
</head>
<body x-data="adminApp()" x-init="init()" x-cloak>

    <template x-if="newUserNotification">
        <div class="notification-toast bg-white border-l-4 border-yellow-500 shadow-2xl p-4 rounded-xl flex items-center space-x-4 max-w-sm">
            <div class="bg-yellow-100 p-2 rounded-full">
                <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
            </div>
            <div>
                <p class="text-[10px] font-black text-gray-400 uppercase">New Registration!</p>
                <p class="text-sm font-bold text-green-900" x-text="newUserName + ' amejiunga sasa hivi'"></p>
            </div>
            <button @click="newUserNotification = false" class="text-gray-400 hover:text-gray-600">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
    </template>

    <template x-if="!session">
        <div class="flex items-center justify-center min-h-screen bg-[#061a06]">
            <div class="max-w-md w-full bg-white/10 backdrop-blur-lg p-10 rounded-[2.5rem] text-center border border-white/10">
                <img src="{img_data}" class="w-24 h-24 rounded-full mx-auto mb-6 border-2 border-yellow-400 shadow-2xl">
                <h2 class="text-2xl font-black text-white uppercase mb-8">Master Admin</h2>
                <div class="space-y-4">
                    <input type="text" x-model="loginData.user" placeholder="Username" class="w-full p-4 rounded-2xl bg-white text-gray-900 outline-none">
                    <input type="password" x-model="loginData.pass" placeholder="Password" class="w-full p-4 rounded-2xl bg-white text-gray-900 outline-none">
                    <button @click="login" class="w-full gradient-green text-yellow-400 py-4 rounded-2xl font-black tracking-widest uppercase shadow-lg">Login</button>
                </div>
            </div>
        </div>
    </template>

    <template x-if="session">
        <div class="min-h-screen flex flex-col">
            <nav class="bg-white border-b h-20 px-6 flex justify-between items-center sticky top-0 z-40">
                <div class="flex items-center space-x-3">
                    <img src="{img_data}" class="w-10 h-10 rounded-full border-2 border-yellow-400">
                    <span class="font-black text-green-900">MASTER ADMIN</span>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="relative">
                         <svg class="w-6 h-6 text-green-800" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
                         <div x-show="newUserNotification" class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white"></div>
                    </div>
                    <button @click="logout" class="text-xs font-bold text-red-600 uppercase">Logout</button>
                </div>
            </nav>

            <main class="p-6 max-w-7xl mx-auto w-full">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="bg-white p-8 rounded-[2rem] border-l-4 border-yellow-500 shadow-sm">
                        <p class="text-[10px] font-black text-gray-400 uppercase">Total Vyuo</p>
                        <h2 class="text-4xl font-black text-green-900" x-text="allVyuo.length">0</h2>
                    </div>
                    <div class="bg-white p-8 rounded-[2rem] border-l-4 border-green-600 shadow-sm">
                        <p class="text-[10px] font-black text-gray-400 uppercase">Viongozi Waliojiunga</p>
                        <h2 class="text-4xl font-black text-green-700" x-text="allViongozi.length">0</h2>
                    </div>
                </div>
                
                <div class="bg-white rounded-[2rem] shadow-xl overflow-hidden">
                    <div class="p-6 bg-green-50 border-b">
                        <h3 class="font-black text-green-900 uppercase text-sm">Orodha ya Vyuo</h3>
                    </div>
                    <table class="w-full text-left">
                        <thead class="bg-gray-50 text-[10px] font-black uppercase text-gray-500">
                            <tr><th class="p-6">Mkoa</th><th class="p-6">Chuo</th><th class="p-6">UVCCM</th></tr>
                        </thead>
                        <tbody>
                            <template x-for="v in allVyuo" :key="v.id">
                                <tr class="border-b hover:bg-yellow-50/30">
                                    <td class="p-6 font-bold text-green-700" x-text="v.mkoa"></td>
                                    <td class="p-6 font-black text-gray-800" x-text="v.jina_la_chuo"></td>
                                    <td class="p-6"><span :class="v.ina_uvccm ? 'bg-green-100 text-green-700' : 'bg-red-50 text-red-700'" class="px-3 py-1 rounded-full text-[9px] font-black" x-text="v.ina_uvccm ? 'IPO' : 'HAIPO'"></span></td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </div>
            </main>
        </div>
    </template>

    <script>
        const {{ createClient }} = supabase;
        const _supabase = createClient('https://xickklzlmwaobzobwyws.supabase.co', 'sb_publishable_94BpD9gpOpYyWryIhzBjog_kxQRAG4W');

        function adminApp() {{
            return {{
                session: JSON.parse(localStorage.getItem('admin_session')) || null,
                loginData: {{ user: '', pass: '' }},
                allVyuo: [], allViongozi: [],
                newUserNotification: false,
                newUserName: '',
                audio: new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3'),

                async init() {{
                    if(this.session) {{
                        await this.loadAll();
                        this.subscribeToNewUsers();
                    }}
                }},

                async login() {{
                    const {{ data }} = await _supabase.from('watumiaji').select('*').eq('username', this.loginData.user).eq('password', this.loginData.pass).single();
                    if(data) {{
                        this.session = data;
                        localStorage.setItem('admin_session', JSON.stringify(data));
                        location.reload();
                    }} else {{ alert("Mtumiaji hajapatikana!"); }}
                }},

                logout() {{ localStorage.clear(); location.reload(); }},

                async loadAll() {{
                    const [resV, resL] = await Promise.all([
                        _supabase.from('vyuo').select('*').order('mkoa'),
                        _supabase.from('viongozi').select('*')
                    ]);
                    this.allVyuo = resV.data || [];
                    this.allViongozi = resL.data || [];
                }},

                // REALTIME SUBSCRIPTION
                subscribeToNewUsers() {{
                    // Sikiliza mabadiliko kwenye table ya 'viongozi'
                    _supabase
                        .channel('any')
                        .on('postgres_changes', {{ event: 'INSERT', schema: 'public', table: 'viongozi' }}, payload => {{
                            this.showNotification(payload.new.jina_kamili);
                            this.loadAll(); // Refresh data
                        }})
                        .subscribe();
                }},

                showNotification(name) {{
                    this.newUserName = name;
                    this.newUserNotification = true;
                    this.audio.play(); // Cheza sauti ya notification
                    
                    // Ficha baada ya sekunde 8
                    setTimeout(() => {{
                        this.newUserNotification = false;
                    }}, 8000);
                }}
            }}
        }}
    </script>
</body>
</html>
"""

components.html(full_custom_code, height=1200, scrolling=True)
