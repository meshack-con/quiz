import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# 1. Page Configuration (Hii ni kwa ajili ya Browser Tab)
st.set_page_config(
    page_title="Master Admin", 
    page_icon="meshack.png", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. Kazi ya kusoma picha na kuibadili kuwa Base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_raw = get_base64_image("meshack.png")
img_data = f"data:image/png;base64,{img_raw}" if img_raw else ""

# 3. LALIZIMISHA ICON NA MANIFEST (Hii inatatua tatizo la icon ya Streamlit)
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
        // 1. Badilisha Favicon kinguvu
        var link = document.querySelector("link[rel*='icon']") || document.createElement('link');
        link.type = 'image/png';
        link.rel = 'shortcut icon';
        link.href = '{img_data}';
        document.getElementsByTagName('head')[0].appendChild(link);
        
        // 2. Badilisha Apple Icon kwa iOS
        var appleLink = document.createElement('link');
        appleLink.rel = 'apple-touch-icon';
        appleLink.href = '{img_data}';
        document.getElementsByTagName('head')[0].appendChild(appleLink);

        // 3. Inject Manifest kwa ajili ya PWA (Install)
        var manifestLink = document.createElement('link');
        manifestLink.rel = 'manifest';
        manifestLink.href = 'data:application/manifest+json;base64,{manifest_b64}';
        document.getElementsByTagName('head')[0].appendChild(manifestLink);
    </script>
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .block-container {{padding: 0px !important;}}
        iframe {{border: none !important;}}
    </style>
""", unsafe_allow_html=True)

# 4. FULL SYSTEM CODE (HTML/JS/CSS)
full_custom_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f0f4f0; color: #1a2e1a; margin: 0; padding: 0; overflow-x: hidden; }}
        [x-cloak] {{ display: none !important; }}
        .glass {{ background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); }}
        .gradient-green {{ background: linear-gradient(135deg, #15803d 0%, #166534 100%); }}
        .stat-card {{ border-left: 4px solid #eab308; }}
        .spinner-container {{ position: relative; width: 106px; height: 106px; display: flex; align-items: center; justify-content: center; }}
        .loader-ring {{
            position: absolute; width: 100%; height: 100%; border: 3px solid transparent;
            border-top-color: #eab308; border-right-color: #eab308; border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }}
        @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body x-data="adminApp()" x-init="init()" x-cloak>

    <template x-if="!session">
        <div class="flex items-start justify-center min-h-screen bg-[#061a06] px-4 pt-12 md:pt-20 relative overflow-hidden">
            <div class="absolute w-96 h-96 bg-green-600/20 rounded-full blur-[80px] -top-20 -left-20"></div>
            <div class="max-w-md w-full glass p-8 md:p-10 rounded-[2.5rem] shadow-2xl text-center z-10 border border-green-900/10">
                <div class="flex justify-center mb-6">
                    <div class="spinner-container">
                        <div x-show="isLoading" class="loader-ring"></div>
                        <img src="{img_data}" class="w-24 h-24 rounded-full object-cover border-2 border-yellow-400 shadow-xl transition-transform" :class="isLoading ? 'scale-90' : ''">
                    </div>
                </div>
                <h2 class="text-2xl font-extrabold text-green-900 mb-1 uppercase">Master Admin</h2>
                <p class="text-[10px] font-black text-green-700 uppercase tracking-widest mb-8">Management System</p>
                
                <div class="space-y-4 text-left">
                    <input type="text" x-model="loginData.user" placeholder="Username" class="w-full p-4 bg-green-50 border border-green-100 rounded-2xl outline-none focus:ring-2 focus:ring-green-500 font-semibold">
                    <input type="password" x-model="loginData.pass" placeholder="Password" class="w-full p-4 bg-green-50 border border-green-100 rounded-2xl outline-none focus:ring-2 focus:ring-green-500 font-semibold">
                    <button @click="login" :disabled="isLoading" class="w-full gradient-green text-yellow-400 py-4 rounded-2xl font-bold shadow-lg uppercase tracking-widest disabled:opacity-50">
                        <span x-text="isLoading ? 'VERIFYING...' : 'LOGIN TO SYSTEM'"></span>
                    </button>
                </div>
            </div>
        </div>
    </template>

    <template x-if="session">
        <div class="min-h-screen flex flex-col">
            <nav class="glass border-b border-green-100 h-20 px-4 md:px-12 flex justify-between items-center sticky top-0 z-50">
                <div class="flex items-center space-x-3">
                    <img src="{img_data}" class="w-10 h-10 rounded-full border-2 border-yellow-400">
                    <span class="font-black text-green-900 uppercase">Master Admin</span>
                </div>
                <button @click="logout" class="bg-red-50 px-4 py-2 rounded-xl text-red-700 font-bold text-[10px] uppercase">Logout</button>
            </nav>

            <main class="max-w-7xl mx-auto w-full px-4 py-8">
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div class="bg-white p-6 rounded-[2rem] shadow-sm stat-card">
                        <p class="text-[10px] font-black text-green-600/50 uppercase mb-2">Total Vyuo</p>
                        <h3 class="text-3xl font-black text-green-900" x-text="allVyuo.length">0</h3>
                    </div>
                    <div class="bg-white p-6 rounded-[2rem] shadow-sm stat-card">
                        <p class="text-[10px] font-black text-green-600/50 uppercase mb-2">UVCCM</p>
                        <h3 class="text-3xl font-black text-green-700" x-text="allVyuo.filter(v => v.ina_uvccm).length">0</h3>
                    </div>
                </div>

                <div class="bg-green-900 p-6 rounded-[2.5rem] shadow-xl mb-8">
                    <label class="text-[10px] font-black text-yellow-400 uppercase mb-2 block">Chujio la Mkoa</label>
                    <select x-model="selectedRegion" @change="applyFilter" class="w-full bg-green-800 text-white p-4 rounded-2xl border-none outline-none font-bold">
                        <option value="ALL">Mikoa Yote</option>
                        <template x-for="m in uniqueMikoa" :key="m"><option :value="m" x-text="m"></option></template>
                    </select>
                </div>

                <div class="bg-white rounded-[2rem] shadow-xl overflow-hidden">
                    <div class="p-6 border-b flex justify-between items-center">
                        <div class="flex space-x-2">
                             <button @click="tab = 'vyuo'" :class="tab === 'vyuo' ? 'bg-green-700 text-yellow-400' : 'text-green-800'" class="px-4 py-2 rounded-lg text-xs font-black uppercase">Vyuo</button>
                             <button @click="tab = 'baraza'" :class="tab === 'baraza' ? 'bg-green-700 text-yellow-400' : 'text-green-800'" class="px-4 py-2 rounded-lg text-xs font-black uppercase">Baraza</button>
                        </div>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead class="bg-green-50 text-[10px] font-black uppercase">
                                <tr><th class="p-6">Mkoa</th><th class="p-6">Jina la Chuo</th><th class="p-6">Hali</th></tr>
                            </thead>
                            <tbody>
                                <template x-for="v in filteredVyuo" :key="v.id">
                                    <tr class="border-b">
                                        <td class="p-6 font-bold text-green-700" x-text="v.mkoa"></td>
                                        <td class="p-6 font-black text-green-900" x-text="v.jina_la_chuo"></td>
                                        <td class="p-6"><span x-text="v.ina_uvccm ? 'IPO' : 'HAIPO'" :class="v.ina_uvccm ? 'bg-green-100 text-green-700' : 'bg-red-50 text-red-700'" class="px-3 py-1 rounded-full text-[9px] font-black"></span></td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    </template>

    <script>
        const {{ createClient }} = supabase;
        const client = createClient('https://xickklzlmwaobzobwyws.supabase.co', 'sb_publishable_94BpD9gpOpYyWryIhzBjog_kxQRAG4W');

        function adminApp() {{
            return {{
                session: JSON.parse(localStorage.getItem('admin_session')) || null,
                isLoading: false, tab: 'vyuo',
                loginData: {{ user: '', pass: '' }},
                selectedRegion: 'ALL',
                uniqueMikoa: [], allVyuo: [], filteredVyuo: [],

                async init() {{ if(this.session) await this.loadAll(); }},

                async login() {{
                    this.isLoading = true;
                    try {{
                        const {{ data }} = await client.from('watumiaji').select('*').eq('username', this.loginData.user).eq('password', this.loginData.pass).single();
                        if(data) {{ 
                            this.session = data; 
                            localStorage.setItem('admin_session', JSON.stringify(data)); 
                            await this.loadAll(); 
                        }} else {{ alert("Login Failed!"); }}
                    }} finally {{ this.isLoading = false; }}
                }},

                logout() {{ localStorage.clear(); location.reload(); }},

                async loadAll() {{
                    const {{ data }} = await client.from('vyuo').select('*').order('mkoa');
                    this.allVyuo = data || [];
                    this.uniqueMikoa = [...new Set(this.allVyuo.map(v => v.mkoa))];
                    this.applyFilter();
                }},

                applyFilter() {{
                    this.filteredVyuo = this.selectedRegion === 'ALL' ? this.allVyuo : this.allVyuo.filter(v => v.mkoa === this.selectedRegion);
                }}
            }}
        }}
    </script>
</body>
</html>
"""

components.html(full_custom_code, height=1200, scrolling=True)
