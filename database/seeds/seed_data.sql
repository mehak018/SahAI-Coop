-- =============================================================================
-- SahAI-Coop Seed Data
-- Target Database: sahai_coop_db
-- Populates Knowledge Base / Sample Responses (English, Hindi, Marathi)
-- and initial demo user/session.
-- =============================================================================

USE `sahai_coop_db`;

-- -----------------------------------------------------------------------------
-- Seed Sample Responses / Knowledge Base
-- Topics: Crop Insurance (PMFBY), PACS Services, Required Documents,
-- Grievance Assistance, Cooperative Society Rules, Government Schemes
-- -----------------------------------------------------------------------------

-- Clear existing sample records to prevent duplicates during repeated seeding
DELETE FROM `sample_responses`;

INSERT INTO `sample_responses` 
(`topic_keyword`, `question_pattern`, `answer_text`, `language`, `source_title`, `source_url`)
VALUES
-- 1. CROP INSURANCE (PMFBY) - English
(
    'Crop Insurance',
    'crop insurance apply pmfby claim premium loss damaged',
    'You can enrol in PMFBY through your bank/PACS, a Common Service Centre (CSC), or the pmfby.gov.in portal before the notified cut-off date for the season. Farmers generally pay a small share of the premium (about 2% for Kharif crops, 1.5% for Rabi food and oilseed crops, and 5% for commercial/horticultural crops). If crops are damaged due to localized calamity or post-harvest losses, report the loss within 72 hours via the Crop Insurance mobile app, the national helpline 14447, or your local agriculture officer.',
    'en',
    'PMFBY – Pradhan Mantri Fasal Bima Yojana • Dept. of Agriculture & Farmers Welfare',
    'https://pmfby.gov.in'
),
-- CROP INSURANCE (PMFBY) - Hindi
(
    'Crop Insurance',
    'फसल बीमा योजना पीएमएफबीवाई आवेदन प्रीमियम नुकसान क्लेम',
    'आप अपने बैंक/पैक्स (PACS), जन सेवा केंद्र (CSC) या pmfby.gov.in पोर्टल के माध्यम से फसल बीमा के लिए आवेदन कर सकते हैं। किसानों को खरीफ फसलों के लिए मात्र 2%, रबी फसलों के लिए 1.5% और वाणिज्यिक/बागवानी फसलों के लिए 5% प्रीमियम देना होता है। फसल क्षति की स्थिति में 72 घंटे के भीतर क्रॉप इंश्योरेंस ऐप या किसान हेल्पलाइन 14447 पर सूचना दर्ज कराएं।',
    'hi',
    'प्रधानमंत्री फसल बीमा योजना (PMFBY) • कृषि एवं किसान कल्याण विभाग',
    'https://pmfby.gov.in'
),
-- CROP INSURANCE (PMFBY) - Marathi
(
    'Crop Insurance',
    'पीक विमा अर्ज पीएमएफबीवाय नुकसान भरपाई हप्ता क्लेम',
    'तुम्ही तुमच्या बँक/PACS, आपले सरकार सेवा केंद्र (CSC) किंवा pmfby.gov.in पोर्टलद्वारे पीक विम्यासाठी नोंदणी करू शकता. खरीप पिकांसाठी 2%, रब्बी पिकांसाठी 1.5% आणि बागायती पिकांसाठी 5% इतका कमी हप्ता शेतकऱ्यांना भरावा लागतो. पिकाचे नुकसान झाल्यास 72 तासांच्या आत पीक विमा ॲप किंवा राष्ट्रीय हेल्पलाइन 14447 द्वारे तक्रार नोंदवणे बंधनकारक आहे.',
    'mr',
    'प्रधानमंत्री पीक विमा योजना (PMFBY) • कृषी व शेतकरी कल्याण मंत्रालय',
    'https://pmfby.gov.in'
),

-- 2. PACS SERVICES - English
(
    'PACS Services',
    'pacs services loan fertilizer seeds credit primary agricultural cooperative society',
    'Primary Agricultural Credit Societies (PACS) provide short-term crop loans (at concessional interest rates via KCC), quality seeds, subsidized fertilizers, agricultural implements, and warehousing facilities at the village level. Computerized PACS also act as Common Service Centres (CSCs) offering digital citizen services, banking correspondence, and direct procurement centers for food grains.',
    'en',
    'Ministry of Cooperation, Government of India • PACS Digitalization Guidelines',
    'https://cooperation.gov.in'
),
-- PACS SERVICES - Hindi
(
    'PACS Services',
    'पैक्स सेवाएं ऋण खाद बीज प्राथमिक कृषि ऋण समिति पैक्स क्या है',
    'प्राथमिक कृषि ऋण समितियां (PACS) ग्राम स्तर पर किसानों को केसीसी (KCC) के माध्यम से रियायती ब्याज दर पर अल्पावधि फसली ऋण, उच्च गुणवत्ता वाले बीज, सब्सिडी वाली खाद और कृषि उपकरण उपलब्ध कराती हैं। कम्प्यूटरीकृत पैक्स अब जन सेवा केंद्र (CSC) और खाद्यान्न खरीद केंद्र के रूप में भी कार्य कर रही हैं।',
    'hi',
    'सहकारिता मंत्रालय, भारत सरकार • पैक्स कम्प्यूटरीकरण दिशा-निर्देश',
    'https://cooperation.gov.in'
),
-- PACS SERVICES - Marathi
(
    'PACS Services',
    'पॅक्स सेवा कर्ज खते बियाणे प्राथमिक कृषी पतसंस्था पॅक्स म्हणजे काय',
    'प्राथमिक कृषी पतसंस्था (PACS) गाव पातळीवर शेतकऱ्यांना किसान क्रेडिट कार्ड (KCC) द्वारे सवलतीच्या दरात अल्पमुदत पीक कर्ज, दर्जेदार खते, बियाणे आणि शेती अवजारे पुरवतात. संगणकीकृत पॅक्स आता सीएससी (CSC) आणि धान्य खरेदी केंद्र म्हणूनही सेवा देतात.',
    'mr',
    'सहकार मंत्रालय, भारत सरकार • पॅक्स संगणकीकरण मार्गदर्शक तत्त्वे',
    'https://cooperation.gov.in'
),

-- 3. REQUIRED DOCUMENTS - English
(
    'Required Documents',
    'documents required kcc crop loan land records aadhar 7/12 passbook apply',
    'Commonly required documents for cooperative society membership, crop insurance, and agricultural loans include: (1) Aadhaar Card for identity proof, (2) Land record ownership proofs (such as 7/12 extract, 8A, or land holding certificate), (3) Bank passbook copy with clear IFSC and account number, (4) Sowing certificate / Crop declaration signed by the village accountant (Talathi/Patwari), and (5) Recent passport size photographs.',
    'en',
    'National Cooperative Development Corporation (NCDC) Guidelines',
    'https://www.ncdc.in'
),
-- REQUIRED DOCUMENTS - Hindi
(
    'Required Documents',
    'आवश्यक दस्तावेज कागजात खतौनी आधार कार्ड बैंक पासबुक केसीसी दस्तावेज',
    'सहकारी समिति सदस्यता, फसल बीमा और केसीसी ऋण के लिए आवश्यक मुख्य दस्तावेज: (1) आधार कार्ड (पहचान व पते का प्रमाण), (2) भू-अभिलेख/खसरा-खतौनी नकल, (3) बैंक पासबुक की प्रति (IFSC कोड सहित), (4) पटवारी/कृषि सहायक द्वारा प्रमाणित बुवाई प्रमाण पत्र, और (5) पासपोर्ट साइज फोटोग्राफ।',
    'hi',
    'राष्ट्रीय सहकारी विकास निगम (NCDC) पोर्टल',
    'https://www.ncdc.in'
),
-- REQUIRED DOCUMENTS - Marathi
(
    'Required Documents',
    'आवश्यक कागदपत्रे ७/१२ उतारा आधार कार्ड बँक पासबुक पीक पेरा दाखला',
    'सहकारी संस्था सभासदत्व, पीक विमा आणि कर्जासाठी लागणारी कागदपत्रे: (१) आधार कार्ड, (२) जमिनीचा चालू ७/१२ आणि ८-अ उतारा, (३) बँक पासबुक प्रत (IFSC कोडसह), (४) तलाठी यांनी दिलेला चालू हंगामाचा पीक पेरा दाखला, आणि (५) २ पासपोर्ट आकाराची छायाचित्रे.',
    'mr',
    'महाराष्ट्र सहकार विभाग • शासकीय सेवा केंद्र',
    'https://cooperation.maharashtra.gov.in'
),

-- 4. GRIEVANCE ASSISTANCE - English
(
    'Grievance Assistance',
    'grievance complain cooperative society dispute illegal fraud registrar help',
    'If you have a complaint regarding a cooperative society (such as loan rejection without cause, delayed insurance payout, election irregularities, or financial misappropriation), you can: (1) Lodge a formal written complaint with the District Registrar of Cooperative Societies, (2) File an online grievance on the CPGRAMS portal (pgportal.gov.in), or (3) Escalate to the State Cooperative Tribunal / Lokayukta.',
    'en',
    'Central Public Grievance Redress and Monitoring System (CPGRAMS)',
    'https://pgportal.gov.in'
),
-- GRIEVANCE ASSISTANCE - Hindi
(
    'Grievance Assistance',
    'शिकायत निवारण सहकारी समिति शिकायत रजिस्ट्रार विवाद धोखाधड़ी',
    'यदि आपको सहकारी समिति से संबंधित कोई शिकायत है (जैसे अकारण ऋण अस्वीकृति, बीमा राशि में देरी, या अनियमितता), तो आप: (1) जिला सहायक निबंधक/रजिस्ट्रार (सहकारी समितियां) को लिखित शिकायत दें, (2) केंद्रीय लोक शिकायत पोर्टल (pgportal.gov.in) पर ऑनलाइन शिकायत दर्ज करें, या (3) राज्य सहकारिता न्यायाधिकरण में अपील करें।',
    'hi',
    'केंद्रीय लोक शिकायत निवारण एवं निगरानी प्रणाली (CPGRAMS)',
    'https://pgportal.gov.in'
),
-- GRIEVANCE ASSISTANCE - Marathi
(
    'Grievance Assistance',
    'तक्रार निवारण सहकारी संस्था तक्रार निबंधक गैरव्यवहार दाद मागणे',
    'सहकारी संस्थेविरुद्ध तक्रार असल्यास (उदा. विनाकारण कर्ज नाकारणे, गैरव्यवहार किंवा निवडणूक अनियमितता), आपण: (१) तालुका किंवा जिल्हा उपनिबंधक सहकारी संस्था (DDR) यांच्याकडे लेखी तक्रार करू शकता, (२) महाराष्ट्र शासनाच्या आपले सरकार तक्रार निवारण पोर्टलवर किंवा CPGRAMS (pgportal.gov.in) वर ऑनलाइन तक्रार नोंदवू शकता.',
    'mr',
    'आपले सरकार तक्रार निवारण प्रणाली • महाराष्ट्र शासन',
    'https://grievances.maharashtra.gov.in'
),

-- 5. COOPERATIVE SOCIETY RULES - English
(
    'Cooperative Society Rules',
    'cooperative society rules bylaws membership rights voting general body meeting',
    'Under the Multi-State Cooperative Societies Act and State Cooperative Societies Acts, every valid member has equal voting rights (one member, one vote). Members have the statutory right to inspect society bylaws, attend Annual General Body Meetings (AGM), audit reports, profit-sharing dividends, and elect managing committee members. Managing committees must hold mandatory periodic meetings and maintain transparent financial books.',
    'en',
    'Multi-State Co-operative Societies Act, 2002 & Amendments',
    'https://mscs.dac.gov.in'
),
-- COOPERATIVE SOCIETY RULES - Hindi
(
    'Cooperative Society Rules',
    'सहकारी समिति नियम उपनियम सदस्यता अधिकार मतदान वार्षिक साधारण सभा',
    'सहकारी समिति अधिनियम के अनुसार प्रत्येक सक्रिय सदस्य को "एक सदस्य, एक वोट" का लोकतांत्रिक अधिकार प्राप्त है। सदस्यों को समिति के उपनियमों की प्रति देखने, वार्षिक आम बैठक (AGM) में भाग लेने, लेखापरीक्षित वित्तीय विवरणों की जांच करने तथा लाभांश प्राप्त करने का कानूनी अधिकार है।',
    'hi',
    'बहु-राज्य सहकारी समितियां अधिनियम एवं नियम',
    'https://mscs.dac.gov.in'
),
-- COOPERATIVE SOCIETY RULES - Marathi
(
    'Cooperative Society Rules',
    'सहकारी संस्था नियम उपविधी सभासद हक्क मतदान वार्षिक सर्वसाधारण सभा',
    'महाराष्ट्र सहकारी संस्था कायदा १९६० नुसार प्रत्येक सभासदाला "एक व्यक्ती, एक मत" चा अधिकार आहे. सभासदांना संस्थेचे उपविधी (By-laws) पाहणे, वार्षिक सर्वसाधारण सभेत (AGM) मत मांडणे, संस्थेचे हिशोब तपासणे आणि लाभांश मिळवण्याचा पूर्ण कायदेशीर अधिकार आहे.',
    'mr',
    'महाराष्ट्र सहकारी संस्था अधिनियम १९६०',
    'https://cooperation.maharashtra.gov.in'
),

-- 6. GOVERNMENT SCHEMES - English
(
    'Government Schemes',
    'government schemes pm kisan subsidy ahidf ncdc interest subvention',
    'Key government schemes for farmers and cooperatives include: (1) PM-KISAN (direct income support of Rs 6,000/year in three instalments), (2) Agriculture Infrastructure Fund (AIF) providing 3% interest subvention for post-harvest infrastructure and cold chains, (3) PM Formalisation of Micro food processing Enterprises (PMFME), and (4) NCDC Yuva Sahakar and Ayushman Sahakar credit schemes.',
    'en',
    'Ministry of Agriculture & Farmers Welfare • Welfare Schemes Portal',
    'https://agricoop.nic.in'
),
-- GOVERNMENT SCHEMES - Hindi
(
    'Government Schemes',
    'सरकारी योजनाएं पीएम किसान सब्सिडी कृषि अवसंरचना कोष ब्याज छूट',
    'किसानों और सहकारी समितियों के लिए प्रमुख सरकारी योजनाएं: (1) पीएम-किसान (प्रत्येक पात्र किसान को सालाना 6,000 रुपये प्रत्यक्ष सहायता), (2) कृषि अवसंरचना कोष (AIF) के तहत 3% ब्याज छूट पर वेयरहाउस व कोल्ड स्टोरेज हेतु ऋण, और (3) पीएम एफएमई (सूक्ष्म खाद्य प्रसंस्करण उद्यम) सब्सिडी योजना।',
    'hi',
    'कृषि एवं किसान कल्याण मंत्रालय • सरकारी योजनाएं',
    'https://agricoop.nic.in'
),
-- GOVERNMENT SCHEMES - Marathi
(
    'Government Schemes',
    'शासकीय योजना पीएम किसान अनुदान व्याज सवलत कृषी पायाभूत सुविधा',
    'शेतकरी आणि सहकारी संस्थांसाठी प्रमुख शासकीय योजना: (१) पीएम-किसान योजना (वार्षिक ६,००० रुपये थेट मदत), (२) कृषी पायाभूत सुविधा निधी (AIF) ३% व्याज सवलतीसह गोदाम व प्रक्रिया केंद्रासाठी कर्ज, आणि (३) नमो शेतकरी महासन्मान निधी योजना (महाराष्ट्र शासनाकडून अतिरिक्त ६,००० रुपये).',
    'mr',
    'कृषी व पदुम विभाग, महाराष्ट्र शासन',
    'https://krishi.maharashtra.gov.in'
);

-- -----------------------------------------------------------------------------
-- Seed Initial Demo User & Initial Conversation (Optional Demo Data)
-- Password for demo user is 'Farmer@123' hashed with bcrypt
-- -----------------------------------------------------------------------------
INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `preferred_language`)
VALUES (
    1, 
    'Ramesh Patil', 
    'ramesh.patil@example.com', 
    '$2b$12$uxKs9WD3xjn0DFeQrQt0zODoNq7O67x9frgvV95upCntRdKncyrci', 
    'en'
) ON DUPLICATE KEY UPDATE `name`=VALUES(`name`), `password_hash`=VALUES(`password_hash`);

INSERT INTO `chat_sessions` (`id`, `user_id`, `title`)
VALUES (
    1, 
    1, 
    'Crop Insurance Inquiry'
) ON DUPLICATE KEY UPDATE `title`=VALUES(`title`);

INSERT INTO `messages` (`id`, `session_id`, `sender`, `content`, `language`, `topic_category`, `source_reference`)
VALUES 
(
    1,
    1,
    'user',
    'How do I apply for crop insurance?',
    'en',
    'Crop Insurance',
    NULL
),
(
    2,
    1,
    'bot',
    'You can enrol in PMFBY through your bank/PACS, a Common Service Centre (CSC), or the pmfby.gov.in portal before the notified cut-off date for the season. Farmers generally pay a small share of the premium (about 2% for Kharif crops, 1.5% for Rabi food crops). If crops are damaged, report the loss within 72 hours via the Crop Insurance mobile app or helpline 14447.',
    'en',
    'Crop Insurance (PMFBY)',
    'PMFBY – Pradhan Mantri Fasal Bima Yojana • Dept. of Agriculture & Farmers Welfare (https://pmfby.gov.in)'
) ON DUPLICATE KEY UPDATE `content`=VALUES(`content`);
