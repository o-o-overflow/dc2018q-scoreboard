import PropTypes from 'prop-types';
import React from 'react';

class GameMatrix extends React.Component {
  header() {
    return this.challenges.map(id => <th key={id}>{id}</th>);
  }

  solvedRow(solves) {
    const solved = this.challenges.map((id) => {
      const isSolved = solves.has(id);
      const theClass = isSolved ? 'solved' : 'not-solved';
      const emoji = isSolved ? '✔' : '❌';
      return <td className={theClass} key={id}>{emoji}</td>;
    });
    return solved;
  }

  body() {
    return this.props.teamScoreboardOrder.map(team =>
      (
        <tr key={team.name}>
          <td key={team.name}>{team.name}</td>
          {this.solvedRow(new Set(team.solves))}
        </tr>
      ));
  }

  render() {
    this.challenges = [];
    Object.keys(this.props.challenges).forEach((category) => {
      this.props.challenges[category].forEach(challenge => this.challenges.push(challenge.id));
    });
    this.challenges.sort();

    return (
      <table className="solves">
        <thead>
          <tr>
            <th>Team</th>
            { this.header() }
          </tr>
        </thead>
        <tbody>
          { this.body() }
        </tbody>
      </table>
    );
  }
}
GameMatrix.propTypes = {
  challenges: PropTypes.objectOf(PropTypes.arrayOf(PropTypes.object)).isRequired,
  teamScoreboardOrder: PropTypes.arrayOf(PropTypes.object).isRequired,
};
export default GameMatrix;
