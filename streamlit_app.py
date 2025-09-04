import streamlit as st
import math
import openai

# --- Page Configuration ---
st.set_page_config(
    page_title="Financial Goal Forecaster",
    page_icon="💰",
    layout="centered"
)

# --- API Key Setup in Sidebar ---
# This creates a sidebar where the user can securely enter their API key.
with st.sidebar:
    st.header("Configuration")
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
    st.markdown("---")
    st.markdown("This app helps you forecast your financial goals by analyzing your budget and projecting savings with and without investment returns.")

# --- Main App Logic ---
# The rest of the app will only run if an API key is provided.
if not openai_api_key:
    st.info("Please enter your OpenAI API key in the sidebar to continue.", icon="🗝️")
else:
    openai.api_key = openai_api_key

    # --- Helper Functions ---
    def get_investment_timeline(savings_goal, net_balance):
        """Calculates the timeline to reach a goal with investment."""
        annual_rate = 0.099
        monthly_rate = (1 + annual_rate)**(1/12) - 1
        if monthly_rate == 0 or net_balance <= 0:
            return 0, 0
        try:
            n_months_invested = math.log((savings_goal * monthly_rate / net_balance) + 1) / math.log(1 + monthly_rate)
            years = int(n_months_invested // 12)
            months = int(n_months_invested % 12)
            return years, months
        except (ValueError, ZeroDivisionError):
            return 0, 0

    # --- Main App Interface ---
    st.title("💰 Financial Goal Forecaster")
    st.write("Enter your monthly finances to calculate your budget and project your savings goals.")

    # Using st.form to group inputs and have a single submission button.
    with st.form("budget_form"):
        st.header("Step 1: Your Monthly Finances")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Income")
            primary_income = st.number_input("💵 Primary Income (after tax)", min_value=0.0, step=100.0, value=4000.0)
            additional_income = st.number_input("💰 Additional Income", min_value=0.0, step=50.0, value=200.0)
        with col2:
            st.subheader("Housing & Utilities")
            housing = st.number_input("🏡 Housing (Rent/Mortgage)", min_value=0.0, step=50.0, value=1500.0)
            utilities = st.number_input("💡 Utilities (Electric, etc.)", min_value=0.0, step=10.0, value=150.0)
            internet = st.number_input("💻 Internet Bill", min_value=0.0, step=5.0, value=60.0)
            phone = st.number_input("📱 Phone Bill", min_value=0.0, step=5.0, value=70.0)
        st.subheader("Living Expenses")
        col3, col4 = st.columns(2)
        with col3:
            groceries = st.number_input("🛒 Groceries", min_value=0.0, step=25.0, value=400.0)
            transportation = st.number_input("🚗 Transportation (Gas, Transit)", min_value=0.0, step=10.0, value=150.0)
            insurance = st.number_input("🛡️ Insurance (Car, Health)", min_value=0.0, step=10.0, value=200.0)
        with col4:
            subscriptions = st.number_input("📺 Subscriptions", min_value=0.0, step=5.0, value=40.0)
            dining_out = st.number_input("🍔 Dining Out / Entertainment", min_value=0.0, step=25.0, value=250.0)
            other = st.number_input("🛍️ Other Spending", min_value=0.0, step=25.0, value=150.0)

        submitted = st.form_submit_button("Calculate My Budget")

    # --- Calculations and Display Logic ---
    if submitted:
        # Perform calculations and store results in session state
        st.session_state.total_income = primary_income + additional_income
        st.session_state.total_expenses = sum([housing, utilities, internet, phone, groceries, transportation, insurance, subscriptions, dining_out, other])
        st.session_state.net_balance = st.session_state.total_income - st.session_state.total_expenses
        st.session_state.budget_calculated = True

    if "budget_calculated" in st.session_state and st.session_state.budget_calculated:
        st.header("Step 2: Your Budget Summary")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Total Income", f"${st.session_state.total_income:,.2f}")
        col2.metric("❌ Total Expenses", f"${st.session_state.total_expenses:,.2f}")
        col3.metric("💰 Net Monthly Savings", f"${st.session_state.net_balance:,.2f}")

        if st.session_state.net_balance > 0:
            st.header("Step 3: Savings Goal Projections")
            
            if st.checkbox("Do you have a specific savings goal you'd like to project?"):
                savings_goal = st.number_input("🎯 What is your savings goal?", min_value=0.0, step=1000.0, value=20000.0)

                if st.button("Project My Goal"):
                    net_balance = st.session_state.net_balance
                    
                    simple_total_months = savings_goal / net_balance
                    simple_years = int(simple_total_months // 12)
                    simple_months = int(simple_total_months % 12)

                    invest_years, invest_months = get_investment_timeline(savings_goal, net_balance)
                    
                    st.subheader("Timelines to Reach Your Goal")
                    col1_res, col2_res = st.columns(2)
                    with col1_res:
                        st.info("**Just Saving**")
                        st.write(f"It would take **{simple_years} years and {simple_months} months**.")
                    with col2_res:
                        st.success("**By Investing** (at 9.9% avg. return)")
                        st.write(f"You could reach it in **{invest_years} years and {invest_months} months**!")

                    st.subheader("🤖 AI Investment Strategist")
                    with st.spinner("Generating personalized investment suggestions..."):
                        ai_prompt = f"""
                        A user has a savings goal of ${savings_goal:,.2f}. Their monthly investment capacity is ${net_balance:,.2f}.
                        Their time horizon without investing is {simple_years} years. Based on this, provide a few educational investment suggestions for an actively managed portfolio.
                        Consider their time horizon for risk tolerance. Suggest a diversified mix of investment types (ETFs, stocks, bonds).
                        Do NOT give specific stock picks. Frame this as educational information and end with a disclaimer about consulting a human professional.
                        """
                        try:
                            response = openai.chat.completions.create(
                                model="gpt-4o",
                                messages=[
                                    {"role": "system", "content": "You are a knowledgeable investment strategist AI."},
                                    {"role": "user", "content": ai_prompt}
                                ]
                            )
                            st.write(response.choices[0].message.content)
                        except Exception as e:
                            st.error(f"An error occurred with the AI model: {e}", icon="🚨")
        else:
            st.error("Your expenses are higher than your income. To project savings, you first need a positive net monthly balance.", icon="⚠️")
