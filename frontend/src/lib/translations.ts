// Translation strings for English and Arabic
export const translations = {
    en: {
        // Landing Page
        landing: {
            title: "ClinTwin",
            subtitle: "Your personal AI pharmacy mirror. Safer medication management at your fingertips.",
            getStarted: "Get Started",
            joinUsers: "Join 50,000+ Safety-First Users",
            instantScan: "Instant AI Scan",
            instantScanDesc: "Identify any pill with just a photo",
            safetyChecks: "Safety Checks",
            safetyChecksDesc: "Cross-reference drug interactions",
            verifiedResults: "Verified Results",
            verifiedResultsDesc: "Trusted data from clinical sources",
            nextGenCare: "Next-Gen Care",
            copyright: "© 2025 ClinTwin. Modernizing Healthcare.",
        },
        // Language Selector
        languageSelector: {
            title: "Choose Your Language",
            titleAr: "اختر لغه للمتابعة",
            english: "English",
            arabic: "العربية",
        },
        // User Type Selection
        userType: {
            title: "Welcome! Please select your role.",
            pharmacyTitle: "Pharmacy Professional",
            pharmacyDesc: "Advanced drug interaction, access to professional dosing guides, quick formulary reference",
            patientTitle: "Patient / Public",
            patientDesc: "Simple medicine identification, easy-to-understand interaction alerts, pill reminders",
            continue: "Continue",
            changeNote: "Don't worry, you can change this later.",
        },
        // Camera Access
        camAccess: {
            title: "To identify Your Medicine, we need camera access",
            subtitle: "Use your camera to scan pills for instant identification. This helps you safely manage your medications.",
            identifyPills: "Identify Pills Instantly",
            checkInteractions: "Check Drug Interactions",
            privacyNote: "All photos and data are processed and stored securely on your device only and are never sent to the cloud.",
            allowAccess: "Allow Camera Access",
            notNow: "Not Now",
        },
        // Home
        home: {
            appName: "ClinTwin",
            greeting: "Good Morning, User",
            identifyByPhoto: "Identify by Photo",
            identifyByPhotoDesc: "Use your camera to scan a pill",
            identifyByDescription: "Identify by Description",
            identifyByDescriptionDesc: "Answer a few simple questions",
            checkInteractions: "Check Interactions",
            checkInteractionsDesc: "Check for harmful drug combinations",
            errorsPrevented: "1M+ medication errors prevented",
            joinUsers: "Join thousands of users staying safe.",
            recentActivity: "Your Recent Activity",
            identifiedViaPhoto: "Identified via Photo",
            interactionCheck: "Interaction Check",
            emergency: "Emergency",
        },
    },
    ar: {
        // Landing Page
        landing: {
            title: "كلين توين",
            subtitle: "مرآتك الصيدلانية الذكية. إدارة أكثر أمانًا للأدوية في متناول يدك.",
            getStarted: "ابدأ الآن",
            joinUsers: "انضم إلى أكثر من 50,000 مستخدم يضعون السلامة أولاً",
            instantScan: "مسح فوري بالذكاء الاصطناعي",
            instantScanDesc: "تعرف على أي حبة دواء بمجرد التقاط صورة",
            safetyChecks: "فحوصات السلامة",
            safetyChecksDesc: "التحقق من التفاعلات الدوائية",
            verifiedResults: "نتائج موثقة",
            verifiedResultsDesc: "بيانات موثوقة من مصادر سريرية",
            nextGenCare: "رعاية الجيل القادم",
            copyright: "© 2025 كلين توين. تحديث الرعاية الصحية.",
        },
        // Language Selector
        languageSelector: {
            title: "اختر لغتك",
            titleAr: "اختر لغه للمتابعة",
            english: "English",
            arabic: "العربية",
        },
        // User Type Selection
        userType: {
            title: "مرحبًا! الرجاء اختيار دورك.",
            pharmacyTitle: "صيدلي محترف",
            pharmacyDesc: "تفاعلات دوائية متقدمة، الوصول إلى أدلة الجرعات المهنية، مرجع سريع للأدوية",
            patientTitle: "مريض / عامة الناس",
            patientDesc: "تحديد بسيط للأدوية، تنبيهات سهلة الفهم للتفاعلات، تذكيرات بالحبوب",
            continue: "متابعة",
            changeNote: "لا تقلق، يمكنك تغيير هذا لاحقًا.",
        },
        // Camera Access
        camAccess: {
            title: "لتحديد دوائك، نحتاج إلى الوصول إلى الكاميرا",
            subtitle: "استخدم الكاميرا لمسح الحبوب للتعرف الفوري. هذا يساعدك على إدارة أدويتك بأمان.",
            identifyPills: "تحديد الحبوب فورًا",
            checkInteractions: "فحص التفاعلات الدوائية",
            privacyNote: "يتم معالجة جميع الصور والبيانات وتخزينها بشكل آمن على جهازك فقط ولا يتم إرسالها إلى السحابة أبدًا.",
            allowAccess: "السماح بالوصول إلى الكاميرا",
            notNow: "ليس الآن",
        },
        // Home
        home: {
            appName: "كلين توين",
            greeting: "صباح الخير، مستخدم",
            identifyByPhoto: "التعرف بالصورة",
            identifyByPhotoDesc: "استخدم الكاميرا لمسح حبة دواء",
            identifyByDescription: "التعرف بالوصف",
            identifyByDescriptionDesc: "أجب عن بعض الأسئلة البسيطة",
            checkInteractions: "فحص التفاعلات",
            checkInteractionsDesc: "تحقق من التركيبات الدوائية الضارة",
            errorsPrevented: "تم منع أكثر من مليون خطأ دوائي",
            joinUsers: "انضم إلى آلاف المستخدمين الذين يحافظون على سلامتهم.",
            recentActivity: "نشاطك الأخير",
            identifiedViaPhoto: "تم التعرف عليه عبر الصورة",
            interactionCheck: "فحص التفاعل",
            emergency: "طوارئ",
        },
    },
};

export type Language = 'en' | 'ar';
export type TranslationKey = typeof translations.en;
