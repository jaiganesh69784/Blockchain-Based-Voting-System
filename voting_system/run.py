from app.election_winner import app, voter_system, reset_all_votes

if __name__ == '__main__':
    # Reset all voting statuses when server starts
    reset_all_votes()
    app.run(debug=True)