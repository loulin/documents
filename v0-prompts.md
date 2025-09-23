# v0 UI 设计提示词 (v0.dev Prompts)

## 1. 医护端 - 大屏仪表盘 (Clinician Dashboard)

**Prompt:**

```
A dashboard for a medical patient management system, designed for nurses. The dashboard has a top filter bar for searching by patient name, tags, and diagnosis. The main area is divided into four horizontal sections with clear titles and background colors: "Critical Risk" (light red background), "High Risk" (light orange background), "Medium Risk" (light yellow background), and "Low Risk" (light gray background). Inside each section, there are patient cards arranged in a grid. Each patient card is clean and modern, showing the patient's name, age, and primary diagnosis at the top. The middle of the card features a small, minimalist 24-hour blood glucose line chart. The bottom of the card shows a snippet of the latest patient message and a clear "View Chat" button. The overall UI is professional, using a clean sans-serif font like Inter, with a spacious and uncluttered layout. Use icons sparingly to enhance clarity. The color palette should be professional and calming, with the risk colors being distinct but not jarring.
```

## 2. 医护端 - 会话中心 (Clinician - Chat Interface)

**Prompt:**

```
A three-column layout for a medical chat application. The left column is a patient list with a search bar on top; each item shows a patient's name, a message snippet, and a timestamp. The center column is the main chat area, with the current patient's name and risk level displayed in the header. Chat bubbles are clearly distinguished for the patient and the nurse. The right column is an "AI Analysis & Data Panel" divided into collapsible sections: "Patient Snapshot" with key info, "Health Data" with a line chart for vitals over time, and "AI Suggestions" with clickable buttons for quick replies. The design is clean, organized, and professional, using a sans-serif font and a calm color scheme suitable for a healthcare setting.
```

## 3. 医护端 - 健康评估结果页 (Clinician - Assessment Result Page)

**Prompt:**

```
A summary page for a patient health risk assessment in a medical web application. The page title is "[Patient Name]'s Health Risk Assessment Report". The most prominent feature is a large, colored label in the center showing the risk level, for example, a red label with the text "Critical Risk". Below it, the specific risk score is displayed, like "115 Points". Underneath the score, there is a section titled "Key Risk Factors" which lists the main reasons for the score, each with an alert icon, e.g., "History of Myocardial Infarction (Risk x2.0)", "HbA1c > 9.0%". At the bottom of the page, there is a clear call to action with three buttons: a primary button "✓ Enroll in Chronic Care Program", and two secondary buttons "Decide Later" and "Do Not Enroll". The overall design is clean, professional, and focuses on communicating the results clearly to a nurse or doctor.
```

## 4. 患者端 - AI确认卡片 (Patient App - AI Confirmation Card)

**Prompt:**

```
A mobile app UI for a health chat application, designed for elderly users. The screen shows a chat conversation. One of the user's sent messages has a special card attached below it. This card is titled "AI Assistant identified the following health records:". The card has a light, friendly background and lists out structured data with large, clear text and icons. For example: an icon of a dinner plate next to "Diet: 2 Buns, 1 Bowl of Porridge", an icon of a blood drop next to "Blood Glucose: 7.8 mmol/L", and an icon of a dizzy face next to "Feeling: Dizzy". Below the list, there are two large, prominent buttons side-by-side: a "Modify" button and a "Confirm ✓" button. The entire interface uses a large, high-contrast font, and the layout is simple and easy to navigate. The overall aesthetic is clean, trustworthy, and accessible.
```

## 5. 医护端 - 健康评估向导 (Clinician - Health Assessment Wizard)

**Prompt:**

```
A multi-step wizard form UI for a professional medical web application. The UI is for creating a new patient health assessment. At the top, there is a clear progress bar showing the steps: "1. Basic Info", "2. Glycemic Status", "3. Complications", "4. Lifestyle", "5. Finish". The current step is highlighted. The form itself is clean and well-organized, with clear labels and spacious input fields. It uses a mix of dropdowns, radio buttons, and checkboxes. There are conditional fields, for example, a dropdown for "Special Diabetes Type" only appears when "Special Type" is selected in the main diagnosis dropdown. The design is professional, using a modern sans-serif font and a muted color palette suitable for a clinical setting. The focus is on clarity and ease of use for nurses filling out complex information.
```
