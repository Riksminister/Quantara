# ---------- DISPLAY ----------
if st.session_state.results:

    investment = st.number_input("💰 Enter your investment ($)", value=1000, step=100)

    for i, r in enumerate(st.session_state.results):

        move = r["expected_move"]
        label = f"🔥 STRONG {r['signal']}" if r["confidence"] > 85 else r["signal"]

        st.markdown(f"""
### 📊 {r['ticker']}

**{label}**  
Confidence: {r['confidence']}%  

Expected Move: {move}%  
Hold Time: {get_timeframe(move)}

Entry: ${r['entry']}  
Stop Loss: ${r['stop_loss']}  
Take Profit: ${r['take_profit']}
""")

        # 🔥 AI INSIGHT (FIXED - ALWAYS WORKS)
        signal = r.get('signal', 'HOLD')
        confidence = r.get('confidence', 50)
        expected_move = r.get('expected_move', 0)
        risk = r.get('risk', 'Medium')

        st.markdown("### 🧠 AI Insight")
        st.info(generate_reasoning(signal, confidence, expected_move, risk))

        st.progress(int(r["confidence"]))

        profit = profit_sim(investment, move)

        st.markdown(f"💰 **Investment: ${investment}**")
        st.markdown(f"💰 **Potential profit: ${profit:.2f}**")

        if st.button(f"📊 View Chart - {r['ticker']}", key=f"chart_{i}"):
            fig = create_chart(r["ticker"], r["signal"])
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
