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
with st.sidebar:
    st.header("Configuration")
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
    st.markdown("---")
    st.markdown("This app helps you forecast your financial goals by analyzing your budget and projecting savings with and without investment returns.")

# --- Main App Logic ---
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
    st.write("Enter your monthly finances to calculate your budget and start a conversation with your AI financial assistant.")

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

        submitted = st.form_submit_button("Calculate Budget & Start Chat")

    if submitted:
        st.session_state.total_income = primary_income + additional_income
        st.session_state.total_expenses = sum([housing, utilities, internet, phone, groceries, transportation, insurance, subscriptions, dining_out, other])
        st.session_state.net_balance = st.session_state.total_income - st.session_state.total_expenses
        st.session_state.budget_calculated = True
        st.session_state.messages = [] # Clear chat history for new budget

    if "budget_calculated" in st.session_state and st.session_state.budget_calculated:
        st.header("Step 2: Your Budget Summary")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Total Income", f"${st.session_state.total_income:,.2f}")
        col2.metric("❌ Total Expenses", f"${st.session_state.total_expenses:,.2f}")
        col3.metric("💰 Net Monthly Savings", f"${st.session_state.net_balance:,.2f}")

        # Initialize the chat and get the AI's first message
        if not st.session_state.messages:
            with st.spinner("AI assistant is analyzing your budget..."):
                initial_prompt = f"""
                The user has just submitted their budget. Here's the summary:
                - Total Income: ${st.session_state.total_income:,.2f}
                - Total Expenses: ${st.session_state.total_expenses:,.2f}
                - Net Savings: ${st.session_state.net_balance:,.2f}

                Your task is to start the conversation. First, provide a brief, one-sentence analysis of their budget (e.g., "It looks like you have a healthy surplus each month.").
                Then, greet them warmly and suggest a few example questions they can ask to get started. Frame the questions to be helpful, such as:
                - "How can I optimize my discretionary spending?"
                - "Based on my income, what's a reasonable savings goal to aim for?"
                - "Can you explain the 50/30/20 budgeting rule and how it applies to me?"
                """
                
                system_prompt = "You are a friendly and encouraging financial assistant AI. Your goal is to help users understand their budget and explore their financial goals."
                
                messages_for_api = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": initial_prompt}
                ]
                
                response = openai.chat.completions.create(model="gpt-4o", messages=messages_for_api)
                initial_ai_message = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": initial_ai_message})
        
        st.header("Step 3: Chat with Your AI Assistant")

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

       # Optional Savings Goal Tool
        if st.session_state.net_balance > 0:
            with st.expander("Explore a Specific Savings Goal"):
                savings_goal = st.number_input("🎯 Enter a savings goal amount", min_value=0.0, step=1000.0, value=20000.0)
                
                if st.button("Project Goal & Discuss with AI"):
                    net_balance = st.session_state.net_balance
                    simple_total_months = savings_goal / net_balance
                    simple_years = int(simple_total_months // 12)
                    simple_months = int(simple_total_months % 12)
                    invest_years, invest_months = get_investment_timeline(savings_goal, net_balance)
                    
                    # Display timelines immediately
                    st.info(f"**Just Saving:** It would take **{simple_years} years and {simple_months} months**.")
                    st.success(f"**By Investing:** You could reach it in **{invest_years} years and {invest_months} months**!")
                    
                    # --- START: NEW LOGIC ---
                    # Create the new prompt and add it to the chat history
                    goal_prompt = f"Great, I've set a goal of ${savings_goal:,.2f}. Based on the timelines calculated, can you give me some investment advice?"
                    st.session_state.messages.append({"role": "user", "content": goal_prompt})

                    # Immediately call the AI with the new prompt
                    with st.spinner("AI is crafting your investment advice..."):
                        system_prompt = "You are a friendly and encouraging financial assistant AI. You are having a conversation with a user about their budget. Their budget details were provided in the first message."
                        messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                        
                        response = openai.chat.completions.create(model="gpt-4o", messages=messages_for_api)
                        full_response = response.choices[0].message.content
                        
                        # Add the AI's response to the chat history
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    # Rerun to display both the user's new message and the AI's response
                    st.rerun()
                    # --- END: NEW LOGIC ---

        # User chat input
        if prompt := st.chat_input("Ask a question about your budget..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    system_prompt = "You are a friendly and encouraging financial assistant AI. You are having a conversation with a user about their budget. Their budget details were provided in the first message."
                    messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                    
                    response = openai.chat.completions.create(model="gpt-4o", messages=messages_for_api)
                    full_response = response.choices[0].message.content
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
