html
<!DOCTYPE html>
<html lang="vi" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibNest AI - Mobile UI Preview</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        darkBg: '#05070b',
                        panelBg: '#0b101d',
                        cardBg: '#0e1422',
                        borderColor: '#1f2c44',
                        accentRed: '#e53935',
                        accentRedHover: '#d32f2f',
                    }
                }
            }
        }
    </script>
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts Inter -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #05070b;
            color: #f4f5f8;
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 4px;
        }
        ::-webkit-scrollbar-track {
            background: #05070b;
        }
        ::-webkit-scrollbar-thumb {
            background: #1f2c44;
            border-radius: 4px;
        }
        .glow-red-icon {
            box-shadow: 0 0 35px rgba(229, 57, 53, 0.45);
        }
    </style>
</head>
<body class="h-screen flex flex-col justify-between overflow-hidden relative select-none">

    <!-- Topbar Header (Strict Flexbox No-Overflow Layout) -->
    <header class="w-full bg-[#080d1a]/95 backdrop-blur-md border-b border-[#1f2c44] px-2.5 py-2 flex items-center justify-between gap-1.5 z-20 shrink-0">
        <!-- Left: Menu Button -->
        <button id="sidebarToggle" class="w-8 h-8 flex items-center justify-center rounded-xl bg-[#0e1422] border border-[#1f2c44] text-gray-300 active:scale-95 transition shrink-0">
            <i class="fa-solid fa-bars text-xs"></i>
        </button>

        <!-- Center: Model Badge (Truncated) -->
        <div class="relative shrink flex-1 max-w-[140px] xs:max-w-[160px] sm:max-w-[200px]">
            <button id="modelSelectBtn" class="w-full flex items-center justify-between bg-[#0e1422] border border-[#1f2c44] px-2.5 py-1.5 rounded-xl text-gray-200 active:bg-[#162035] transition">
                <span id="selectedModel" class="text-[11px] font-semibold truncate text-gray-200">gemini-3.8-flash</span>
                <i class="fa-solid fa-chevron-down text-[9px] text-gray-400 ml-1 shrink-0"></i>
            </button>
            <div id="modelDropdown" class="hidden absolute top-full left-0 mt-1.5 w-44 bg-[#0b101d] border border-[#1f2c44] rounded-xl shadow-2xl py-1 z-50 text-[11px]">
                <a href="#" onclick="selectModel('gemini-3.8-flash')" class="block px-3 py-2 text-gray-200 hover:bg-[#1f2c44] transition truncate">gemini-3.8-flash</a>
                <a href="#" onclick="selectModel('gpt-4o-mini')" class="block px-3 py-2 text-gray-200 hover:bg-[#1f2c44] transition truncate">gpt-4o-mini</a>
                <a href="#" onclick="selectModel('llama-3.3-70b-versatile')" class="block px-3 py-2 text-gray-200 hover:bg-[#1f2c44] transition truncate">llama-3.3-70b-versatile</a>
            </div>
        </div>

        <!-- Right: Action Buttons -->
        <div class="flex items-center gap-1.5 shrink-0">
            <!-- Giftcode Button -->
            <button onclick="showToast('🎁 Giftcode: VIBNEST2026 đã áp dụng!')" class="flex items-center gap-1 bg-[#0e1422] border border-[#ff4b4b]/40 text-[#ff5252] text-[11px] font-semibold px-2.5 py-1.5 rounded-xl active:scale-95 transition">
                <i class="fa-solid fa-gift text-[10px]"></i>
                <span class="whitespace-nowrap">Giftcode</span>
            </button>

            <!-- Charge Credits Button -->
            <button onclick="openModal()" class="flex items-center gap-1 bg-[#e53935] hover:bg-[#d32f2f] text-white text-[11px] font-bold px-2.5 py-1.5 rounded-xl shadow-md shadow-red-900/40 active:scale-95 transition">
                <i class="fa-solid fa-dollar-sign text-[10px]"></i>
                <span class="whitespace-nowrap">Nạp tín dụng</span>
            </button>
        </div>
    </header>

    <!-- Sidebar Drawer Overlay -->
    <div id="sidebarOverlay" onclick="closeSidebar()" class="hidden fixed inset-0 bg-black/70 backdrop-blur-sm z-30 transition-opacity"></div>

    <!-- Sidebar Drawer Panel -->
    <aside id="sidebar" class="fixed top-0 left-0 bottom-0 w-72 sm:w-80 bg-[#0b101d] border-r border-[#1f2c44] z-40 transform -translate-x-full transition-transform duration-300 flex flex-col justify-between p-4">
        <div>
            <!-- Sidebar Header -->
            <div class="flex items-center justify-between mb-5">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-red-600 to-orange-500 flex items-center justify-center text-white font-bold text-xs">◈</div>
                    <span class="font-bold text-base text-white">VibNest AI</span>
                </div>
                <button onclick="closeSidebar()" class="text-gray-400 hover:text-white p-1">
                    <i class="fa-solid fa-xmark text-base"></i>
                </button>
            </div>

            <!-- New Chat Button -->
            <button onclick="resetChat()" class="w-full bg-[#e53935] hover:bg-[#d32f2f] text-white font-semibold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-2 transition mb-4 shadow-md">
                <i class="fa-solid fa-plus text-xs"></i>
                <span>Cuộc trò chuyện mới</span>
            </button>

            <!-- Recent Chat History -->
            <div class="text-[10px] font-bold text-gray-400 mb-2 uppercase tracking-wider px-1">Lịch sử trò chuyện</div>
            <div class="space-y-1 overflow-y-auto max-h-60 pr-1">
                <button class="w-full text-left px-3 py-2 rounded-xl bg-[#162035] text-white text-xs truncate flex items-center gap-2">
                    <i class="fa-solid fa-message text-red-500 text-[10px]"></i>
                    <span>Tạo giao diện chatbot Streamlit</span>
                </button>
                <button class="w-full text-left px-3 py-2 rounded-xl text-gray-400 hover:bg-[#162035]/50 hover:text-gray-200 text-xs truncate flex items-center gap-2 transition">
                    <i class="fa-regular fa-message text-gray-500 text-[10px]"></i>
                    <span>Cấu hình API Key Gemini</span>
                </button>
            </div>
        </div>

        <!-- Sidebar Banking Info Box -->
        <div class="border-t border-[#1f2c44] pt-3">
            <div class="text-[11px] font-bold text-red-400 mb-1.5 flex items-center gap-1.5">
                <i class="fa-solid fa-gem"></i> Nạp tiền ngân hàng
            </div>
            <div class="bg-[#0e1422] border border-[#1f2c44] rounded-xl p-2.5 text-[11px] space-y-1 text-gray-300">
                <div class="flex justify-between"><span class="text-gray-400">Ngân hàng:</span> <span class="font-semibold text-white">MB Bank</span></div>
                <div class="flex justify-between"><span class="text-gray-400">STK:</span> <span class="font-mono text-amber-300">123456789</span></div>
                <div class="flex justify-between"><span class="text-gray-400">Chủ TK:</span> <span class="font-semibold text-white">CHINH LY</span></div>
                <div class="flex justify-between"><span class="text-gray-400">Nội dung:</span> <span class="font-mono text-red-400">nap VibNest</span></div>
            </div>
        </div>
    </aside>

    <!-- Main Chat Area Container -->
    <main id="chatContainer" class="flex-1 overflow-y-auto max-w-xl w-full mx-auto px-3 py-4 flex flex-col justify-start">

        <!-- Default Hero View when no chat messages -->
        <div id="heroView" class="my-auto flex flex-col items-center justify-center text-center py-6">
            <!-- Red Glowing Devil / AI Logo Icon -->
            <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gradient-to-tr from-red-600 via-red-500 to-orange-500 flex items-center justify-center glow-red-icon mb-4 animate-pulse">
                <i class="fa-solid fa-dragon text-3xl sm:text-4xl text-white"></i>
            </div>
            
            <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight mb-1">WormGPT Ready</h1>
            <p class="text-gray-400 text-xs sm:text-sm">Trợ lý AI của bạn. Hãy bắt đầu trò chuyện!</p>
        </div>

        <!-- Chat Message History Container -->
        <div id="messagesList" class="w-full space-y-3 hidden">
            <!-- Messages populated dynamically via JavaScript -->
        </div>
    </main>

    <!-- Bottom Input Controls Bar -->
    <footer class="w-full max-w-xl mx-auto px-3 pb-3 pt-1 shrink-0 z-10">
        <div class="bg-[#0b101d] border border-[#1f2c44] rounded-2xl p-2 shadow-2xl focus-within:border-red-500/60 transition">
            
            <textarea id="chatInput" rows="1" placeholder="Nhập tin nhắn..." class="w-full bg-transparent text-gray-200 placeholder-gray-500 text-xs sm:text-sm px-2 pt-1 pb-6 focus:outline-none resize-none max-h-28"></textarea>
            
            <!-- Controls Bar inside text area -->
            <div class="flex items-center justify-between pt-1 border-t border-[#162035]/80">
                <div class="flex items-center gap-1.5">
                    <!-- File Attachment Pill -->
                    <button onclick="showToast('Mở hộp thoại đính kèm tập tin')" class="flex items-center gap-1 bg-[#0e1422] border border-[#1f2c44] active:bg-[#162035] text-gray-300 text-[11px] px-2.5 py-1 rounded-xl transition">
                        <i class="fa-solid fa-paperclip text-[10px]"></i>
                        <span>Đính kèm</span>
                    </button>

                    <!-- Agent Toggle Pill -->
                    <button id="agentBtn" onclick="toggleAgent()" class="flex items-center gap-1 bg-[#0e1422] border border-[#1f2c44] text-gray-300 text-[11px] px-2.5 py-1 rounded-xl transition">
                        <i class="fa-solid fa-list-check text-[10px] text-gray-400"></i>
                        <span>Agent</span>
                        <span id="agentBadge" class="bg-red-500/20 text-red-400 font-bold px-1 rounded text-[9px]">BẬT</span>
                    </button>
                </div>

                <!-- Submit Button -->
                <button id="sendBtn" onclick="submitMessage()" class="w-8 h-8 bg-[#e53935] hover:bg-[#d32f2f] text-white rounded-xl flex items-center justify-center active:scale-95 transition shadow-md shadow-red-900/30">
                    <i class="fa-solid fa-arrow-up text-xs"></i>
                </button>
            </div>
        </div>
    </footer>

    <!-- Payment Modal (Banking Dialog) -->
    <div id="paymentModal" class="hidden fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-[#0b101d] border border-[#1f2c44] w-full max-w-xs rounded-2xl p-4 shadow-2xl relative">
            <button onclick="closeModal()" class="absolute top-3 right-3 text-gray-400 hover:text-white">
                <i class="fa-solid fa-xmark text-base"></i>
            </button>
            <div class="text-center mb-3">
                <div class="w-10 h-10 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center mx-auto mb-1.5 text-lg">
                    <i class="fa-solid fa-credit-card"></i>
                </div>
                <h3 class="text-base font-bold text-white">Nạp tín dụng VibNest</h3>
                <p class="text-[10px] text-gray-400">Chuyển khoản theo thông tin bên dưới</p>
            </div>
            <div class="bg-[#0e1422] border border-[#1f2c44] rounded-xl p-2.5 text-[11px] space-y-1.5 text-gray-300 mb-3">
                <div class="flex justify-between"><span>Ngân hàng:</span> <span class="font-bold text-white">MB Bank</span></div>
                <div class="flex justify-between"><span>Số tài khoản:</span> <span class="font-mono text-amber-300 font-bold">123456789</span></div>
                <div class="flex justify-between"><span>Chủ tài khoản:</span> <span class="font-bold text-white">CHINH LY</span></div>
                <div class="flex justify-between"><span>Nội dung CK:</span> <span class="font-mono text-red-400 font-bold">nap VibNest</span></div>
            </div>
            <button onclick="closeModal(); showToast('Đã ghi nhận yêu cầu nạp tiền!');" class="w-full bg-[#e53935] hover:bg-[#d32f2f] text-white font-bold py-2 rounded-xl text-xs transition">
                Tôi đã chuyển khoản
            </button>
        </div>
    </div>

    <!-- Toast Notification Popup -->
    <div id="toast" class="hidden fixed top-12 left-1/2 transform -translate-x-1/2 bg-[#0e1422] border border-red-500/50 text-white text-[11px] px-3.5 py-2 rounded-xl shadow-2xl z-50 flex items-center gap-2 whitespace-nowrap">
        <i class="fa-solid fa-circle-info text-red-400"></i>
        <span id="toastMsg">Notification message</span>
    </div>

    <!-- Interactive Script -->
    <script>
        let agentActive = true;

        // Model selector dropdown logic
        const modelBtn = document.getElementById('modelSelectBtn');
        const modelDropdown = document.getElementById('modelDropdown');
        modelBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            modelDropdown.classList.toggle('hidden');
        });

        document.addEventListener('click', () => {
            modelDropdown.classList.add('hidden');
        });

        function selectModel(name) {
            document.getElementById('selectedModel').innerText = name;
            modelDropdown.classList.add('hidden');
            showToast(`Đã chuyển sang ${name}`);
        }

        // Sidebar controls
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            sidebar.classList.remove('-translate-x-full');
            sidebarOverlay.classList.remove('hidden');
        });

        function closeSidebar() {
            sidebar.classList.add('-translate-x-full');
            sidebarOverlay.classList.add('hidden');
        }

        // Agent Toggle logic
        function toggleAgent() {
            agentActive = !agentActive;
            const badge = document.getElementById('agentBadge');
            if (agentActive) {
                badge.innerText = 'BẬT';
                badge.className = 'bg-red-500/20 text-red-400 font-bold px-1 rounded text-[9px]';
                showToast('Chế độ Agent đã BẬT');
            } else {
                badge.innerText = 'TẮT';
                badge.className = 'bg-gray-500/20 text-gray-400 font-bold px-1 rounded text-[9px]';
                showToast('Chế độ Agent đã TẮT');
            }
        }

        // Modal controls
        function openModal() {
            document.getElementById('paymentModal').classList.remove('hidden');
        }
        function closeModal() {
            document.getElementById('paymentModal').classList.add('hidden');
        }

        // Toast Notification
        function showToast(msg) {
            const toast = document.getElementById('toast');
            document.getElementById('toastMsg').innerText = msg;
            toast.classList.remove('hidden');
            setTimeout(() => {
                toast.classList.add('hidden');
            }, 2500);
        }

        // Chat Logic
        const chatInput = document.getElementById('chatInput');
        const heroView = document.getElementById('heroView');
        const messagesList = document.getElementById('messagesList');

        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitMessage();
            }
        });

        function submitMessage() {
            const text = chatInput.value.trim();
            if (!text) return;

            heroView.classList.add('hidden');
            messagesList.classList.remove('hidden');

            // Render User Bubble
            const userMsgDiv = document.createElement('div');
            userMsgDiv.className = 'flex flex-col items-end';
            userMsgDiv.innerHTML = `
                <div class="bg-[#e53935] text-white text-xs px-3.5 py-2 rounded-2xl rounded-tr-none max-w-[85%] shadow-md">
                    ${escapeHtml(text)}
                </div>
            `;
            messagesList.appendChild(userMsgDiv);

            chatInput.value = '';
            scrollToBottom();

            // Simulate Assistant Response
            setTimeout(() => {
                const modelName = document.getElementById('selectedModel').innerText;
                const assistantMsgDiv = document.createElement('div');
                assistantMsgDiv.className = 'flex flex-col items-start';
                assistantMsgDiv.innerHTML = `
                    <div class="flex items-center gap-1.5 mb-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                        <span class="text-[10px] text-gray-400 font-semibold">${modelName}</span>
                    </div>
                    <div class="bg-[#0e1422] border border-[#1f2c44] text-gray-200 text-xs px-3.5 py-2.5 rounded-2xl rounded-tl-none max-w-[88%] shadow-md leading-relaxed">
                        Chào bạn! Tôi là trợ lý AI <strong>VibNest</strong> (${modelName}). Tôi đã nhận được yêu cầu của bạn!
                    </div>
                `;
                messagesList.appendChild(assistantMsgDiv);
                scrollToBottom();
            }, 500);
        }

        function resetChat() {
            messagesList.innerHTML = '';
            messagesList.classList.add('hidden');
            heroView.classList.remove('hidden');
            closeSidebar();
            showToast('Đã tạo cuộc trò chuyện mới');
        }

        function scrollToBottom() {
            const container = document.getElementById('chatContainer');
            container.scrollTop = container.scrollHeight;
        }

        function escapeHtml(str) {
            return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        }
    </script>
</body>
</html>
