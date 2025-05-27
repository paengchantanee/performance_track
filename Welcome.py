import streamlit as st

st.title("Welcom to Performance tracking application!👋")
#st.subheader("ยินดีต้อนรับเข้าสู่แอปการติดตามประสิทธิภาพของพนักงาน",divider=True)
st.write("This app is designed for tracking employee performance that includes an evaluation form, employee management features, and an insightful criteria dashboard report.")
st.caption("แอปนี้ทำมาเพื่อใช้ในการติดตามประสิทธิภาพของพนักงานที่ประกอบไปด้วย แบบประเมินพนักงาน ระบบจัดการพนักงาน และรายงานสรุปข้อมูลเชิงลึกที่ได้มาจากการทำแบบประเมิน")

st.subheader("🧑‍💻Why is performance tracking important?")
st.subheader("ทำไมการติดตามประสิทธิภาพของพนักงานถึงสำคัญ?",divider=True)
st.write("- Create more effective goals / สร้างเป้าหมายที่มีประสิทธิผลมากขึ้น\n" \
"- Improve employee productivity / เพิ่มประสิทธิภาพในการทำงานของพนักงาน\n" \
"- Identify training and development needs / ประเมินความจำเป็นในการฝึกอบรมและพัฒนา\n" \
"- Increase engagement with employees / เพิ่มการมีส่วนร่วมกันในหมู่พนักงาน\n" \
"- Boost retention and satisfaction / เสริมสร้างความผูกพันและความพึงพอใจของพนักงาน\n" \
"- Recognize and reward top performers / ยกย่องและให้รางวัลแก่พนักงานที่มีผลงานโดดเด่น")

st.header("🚀How to use this app?")
st.subheader("แอปนี้ใช้อย่างไร?",divider=True)
st.write("👈Select an app from the sidebar / เลือกแอปจากแถบด้านข้าง")
st.write("To fill out the evaluation form, click **'📝Form'**. To manage employee data, click **'👥Employee'**. To view evaluation insights, click **'📊Dashboard'**.")
st.caption("ในการกรอกแบบฟอร์มประเมิน ให้คลิก **'📝Form'** หากต้องการจัดการข้อมูลพนักงาน ให้คลิก **'👥Employee'** และหากต้องการดูผลการประเมินเชิงลึก ให้คลิก **'📊Dashboard'**")
