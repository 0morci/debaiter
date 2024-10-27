import openai
import time
import streamlit as st

class DebateBot:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.conversation_history = []
        

    def generate_response(self, role, topic, stance, previous_argument=None):
        def is_response_complete(text):
            # Check if response ends with proper punctuation
            if not text[-1] in ['.', '!', '?']:
                return False
            
            # Check for common incomplete indicators
            incomplete_phrases = [
                'however,', 'moreover,', 'furthermore,', 'additionally,',
                'therefore,', 'thus,', 'consequently,', 'as a result,',
                'for example,', 'such as', 'including'
            ]
            
            text_lower = text.lower()
            for phrase in incomplete_phrases:
                if text_lower.strip().endswith(phrase):
                    return False
            
            return True

        system_message = f"""You are a passionate debater who {stance} {topic}. 
            Important: Your response must be a complete thought with proper conclusion.
            - Keep responses focused and natural
            - Every argument must be fully completed
            - End with a clear concluding statement
            - Never leave thoughts unfinished
            - Avoid ending with transitional phrases
            - Maximum 2-3 main points per response"""

        max_attempts = 3
        current_attempt = 0
        
        while current_attempt < max_attempts:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": self._create_prompt(role, topic, stance, previous_argument)}
                    ],
                    max_tokens=300,  # Increased for more complete responses
                    temperature=0.8,
                    presence_penalty=0.6,
                    frequency_penalty=0.6,
                )
                
                response_text = response.choices[0].message.content.strip()
                
                # Check if response is complete
                if is_response_complete(response_text):
                    return response_text
                
                # If we're on our last attempt and still incomplete, try to fix it
                if current_attempt == max_attempts - 1:
                    # Try to complete the thought
                    completion_prompt = f"Please complete this thought concisely: {response_text}"
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Complete the thought in one brief sentence."},
                            {"role": "user", "content": completion_prompt}
                        ],
                        max_tokens=50,
                        temperature=0.7
                    )
                    
                    return response_text + " " + completion.choices[0].message.content.strip()
                
                current_attempt += 1
                
            except Exception as e:
                return f"Error generating response: {str(e)}"
        
        return response_text  # Return the best attempt if we couldn't get a perfect response

    def _create_prompt(self, role, topic, stance, previous_argument):
        if previous_argument is None:
            # Opening statement - focus on position and values
            return f"""Present your opening statement about {topic}. 
                      As someone who {stance} this issue:
                      - Express your core position clearly
                      - Explain the key principles behind your stance
                      - Share your general perspective on this matter
                      - Outline the main points you'll defend
                      Keep it conversational and engaging, like starting a meaningful discussion."""
        else:
            # Rebuttal - now we bring in the evidence
            return f"""Respond to this argument about {topic}: '{previous_argument}'
                      Support your rebuttal with:
                      - Relevant data and statistics
                      - Expert opinions or studies
                      - Specific examples and case studies
                      - Analysis of the opposing argument
                      Make your counter-argument compelling and evidence-based."""

    def conduct_debate(self, topic, rounds=3, user_stance=None):
        print(f"\nDebate Topic: {topic}")
        print("=" * 50)
        
        # First round - Opening Statements
        print("\nRound 1 - Opening Statements")
        print("-" * 20)
        
        if user_stance == "proponent":
            # User goes first
            user_input = input("Your opening statement (proponent): ")
            print(f"Proponent (You): {user_input}")
            self.conversation_history.append(user_input)
            
            # AI opponent responds
            con_response = self.generate_response(
                "opponent",
                topic,
                "opposes and argues against",
                None
            )
            print(f"Opponent (AI): {con_response}")
            self.conversation_history.append(con_response)
            
        elif user_stance == "opponent":
            # AI proponent goes first
            pro_response = self.generate_response(
                "proponent",
                topic,
                "supports and advocates for",
                None
            )
            print(f"Proponent (AI): {pro_response}")
            self.conversation_history.append(pro_response)
            
            # User responds
            user_input = input("Your opening statement (opponent): ")
            print(f"Opponent (You): {user_input}")
            self.conversation_history.append(user_input)
        
        else:  # AI vs AI debate
            # Proponent's opening statement
            pro_response = self.generate_response(
                "proponent",
                topic,
                "supports and advocates for",
                None
            )
            print(f"Proponent (AI): {pro_response}")
            self.conversation_history.append(pro_response)
            
            time.sleep(1)  # Prevent rate limiting
            
            # Opponent's opening statement
            con_response = self.generate_response(
                "opponent",
                topic,
                "opposes and argues against",
                None
            )
            print(f"Opponent (AI): {con_response}")
            self.conversation_history.append(con_response)
            
            time.sleep(1)
        
        # Subsequent rounds - Rebuttals
        for round_num in range(2, rounds + 1):
            print(f"\nRound {round_num} - Rebuttals")
            print("-" * 20)
            
            if user_stance == "proponent":
                # User's turn
                user_input = input("Your rebuttal (proponent): ")
                print(f"Proponent (You): {user_input}")
                self.conversation_history.append(user_input)
                
                # AI opponent's turn
                con_response = self.generate_response(
                    "opponent",
                    topic,
                    "opposes and argues against",
                    self.conversation_history[-1]
                )
                print(f"Opponent (AI): {con_response}")
                self.conversation_history.append(con_response)
                
            elif user_stance == "opponent":
                # AI proponent's turn
                pro_response = self.generate_response(
                    "proponent",
                    topic,
                    "supports and advocates for",
                    self.conversation_history[-1]
                )
                print(f"Proponent (AI): {pro_response}")
                self.conversation_history.append(pro_response)
                
                # User's turn
                user_input = input("Your rebuttal (opponent): ")
                print(f"Opponent (You): {user_input}")
                self.conversation_history.append(user_input)
            
            else:  # AI vs AI debate
                # Proponent's rebuttal
                pro_response = self.generate_response(
                    "proponent",
                    topic,
                    "supports and advocates for",
                    self.conversation_history[-1]  # Respond to opponent's last argument
                )
                print(f"Proponent (AI): {pro_response}")
                self.conversation_history.append(pro_response)
                
                time.sleep(1)  # Prevent rate limiting
                
                # Opponent's rebuttal
                con_response = self.generate_response(
                    "opponent",
                    topic,
                    "opposes and argues against",
                    self.conversation_history[-1]  # Respond to proponent's last argument
                )
                print(f"Opponent (AI): {con_response}")
                self.conversation_history.append(con_response)
                
                time.sleep(1)
def main():
    st.title("debaite 🗣")
    st.text("*Disclaimer*: This is an AI debate simulation.")
    st.text("""While the agents attempt to use real statistics and facts, 
the accuracy of specific numbers and claims should be independently verified.""")
    
    # Initialize session state if needed
    if 'debate_bot' not in st.session_state:
        api_key = "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"
        st.session_state.debate_bot = DebateBot(api_key)
        st.session_state.debate_started = False
        st.session_state.current_round = 1
        st.session_state.messages = []

    # Input fields
    topic = st.text_input("Enter the debate topic:")
    role = st.radio(
        "Choose your role:",
        ["Proponent (for the topic)", "Opponent (against the topic)", "Observer (AI vs AI)"],
        key="role"
    )
    rounds = st.slider("Number of rounds:", min_value=1, max_value=10, value=3)

    # Convert role choice to stance
    role_mapping = {
        "Proponent (for the topic)": "proponent",
        "Opponent (against the topic)": "opponent",
        "Observer (AI vs AI)": None
    }
    user_stance = role_mapping[role]

    # Start debate button
    if st.button("Start Debate") and topic:
        # Clear previous debate messages
        st.session_state.messages = []
        st.session_state.debate_bot.conversation_history = []
        st.session_state.debate_started = True
        st.session_state.current_round = 1
        
        # Handle AI vs AI debate
        if user_stance is None:
            # Opening Round
            st.subheader("Round 1: Opening Statements")
            
            # Proponent's opening statement
            with st.spinner("Proponent (AI) is thinking..."):
                pro_response = st.session_state.debate_bot.generate_response(
                    "proponent",
                    topic,
                    "supports and advocates for",
                    None
                )
                st.session_state.messages.append(("Proponent (AI)", pro_response))
                st.write("**Proponent (AI):**", pro_response)
                st.write("---")
            
            # Opponent's opening statement
            with st.spinner("Opponent (AI) is thinking..."):
                con_response = st.session_state.debate_bot.generate_response(
                    "opponent",
                    topic,
                    "opposes and argues against",
                    None
                )
                st.session_state.messages.append(("Opponent (AI)", con_response))
                st.write("**Opponent (AI):**", con_response)
                st.write("---")
            
            # Subsequent rounds
            for round_num in range(2, rounds + 1):
                st.subheader(f"Round {round_num}: Rebuttals")
                
                # Proponent's rebuttal
                with st.spinner(f"Round {round_num}: Proponent (AI) is thinking..."):
                    pro_response = st.session_state.debate_bot.generate_response(
                        "proponent",
                        topic,
                        "supports and advocates for",
                        st.session_state.messages[-1][1]  # Use the last message as context
                    )
                    st.session_state.messages.append(("Proponent (AI)", pro_response))
                    st.write("**Proponent (AI):**", pro_response)
                    st.write("---")
                
                # Opponent's rebuttal
                with st.spinner(f"Round {round_num}: Opponent (AI) is thinking..."):
                    con_response = st.session_state.debate_bot.generate_response(
                        "opponent",
                        topic,
                        "opposes and argues against",
                        st.session_state.messages[-1][1]  # Use the last message as context
                    )
                    st.session_state.messages.append(("Opponent (AI)", con_response))
                    st.write("**Opponent (AI):**", con_response)
                    st.write("---")
            
            st.subheader("Debate Completed!")

    # For human vs AI debates
    if st.session_state.debate_started and user_stance and st.session_state.current_round <= rounds:
        # Display current conversation
        for i in range(0, len(st.session_state.messages), 2):
            if i == 0:
                st.subheader("Round 1: Opening Statements")
            elif i > 0:
                st.subheader(f"Round {(i//2) + 1}: Rebuttals")
            
            # Display the pair of messages for this round
            if i < len(st.session_state.messages):
                st.write(f"{st.session_state.messages[i][0]}: {st.session_state.messages[i][1]}")
                st.write("---")
            if i + 1 < len(st.session_state.messages):
                st.write(f"{st.session_state.messages[i+1][0]}: {st.session_state.messages[i+1][1]}")
                st.write("---")

        # Show current round header
        if len(st.session_state.messages) == 0:
            st.subheader("Round 1: Opening Statements")
        else:
            current_round = (len(st.session_state.messages) // 2) + 1
            st.subheader(f"Round {current_round}: {'Opening Statements' if current_round == 1 else 'Rebuttals'}")
        # User input section
        user_input = st.text_input(
            f"Your {'rebuttal' if st.session_state.current_round > 1 else 'opening statement'} "
            f"({user_stance}):",
            key=f"round_{st.session_state.current_round}"
        )
        if st.button(f"Submit Round {st.session_state.current_round}"):
            if user_input:
                # Add user's message
                speaker = "Proponent (You)" if user_stance == "proponent" else "Opponent (You)"
                st.session_state.messages.append((speaker, user_input))
                
                # Generate AI response
                ai_role = "opponent" if user_stance == "proponent" else "proponent"
                ai_stance = "opposes and argues against" if ai_role == "opponent" else "supports and advocates for"
                
                with st.spinner(f"AI is thinking..."):
                    ai_response = st.session_state.debate_bot.generate_response(
                        ai_role,
                        topic,
                        ai_stance,
                        user_input
                    )
                    ai_speaker = "Opponent (AI)" if ai_role == "opponent" else "Proponent (AI)"
                    st.session_state.messages.append((ai_speaker, ai_response))
                
                st.session_state.current_round += 1
                
                # Display the new messages without rerunning the page
                st.write(f"**{speaker}**: {user_input}")
                st.write("---")
                st.write(f"**{ai_speaker}**: {ai_response}")
                st.write("---")
                
                # Check if debate is over
                if st.session_state.current_round > rounds:
                    st.subheader("Debate Completed!")

if __name__ == "__main__":
    main()
