import PropTypes from 'prop-types';
import React from 'react';

const CATEGORY_TO_CSS_CLASS = {
  'amuse bouche': 'category-amuse',
  appetizers: 'category-appetizers',
  'from the grill': 'category-grill',
  'signature dishes': 'category-signature',
  'guest chefs': 'category-guest',
  'fruits and desserts': 'category-desserts',
};

function categoryIcons(categoryByChallenge, challengeId) {
  const cssClass = CATEGORY_TO_CSS_CLASS[categoryByChallenge[challengeId]];
  return <span className={cssClass} key={challengeId} title={challengeId} />;
}

function Scoreboard(props) {
  let rank = 0;
  const teams = props.teamScoreboardOrder.map((team) => {
    rank += 1;
    return {
      lastSolveTime: team.lastSolveTime,
      name: team.name,
      rank,
      points: props.pointsByTeam[team.name],
      solves: team.solves.map(id => categoryIcons(props.categoryByChallenge, id)),
    };
  });

  const teamRows = teams.map(team =>
    (
      <tr key={team.name} id={team.name} >
        <td>{team.rank}</td>
        <td>{team.name}</td>
        <td>{team.solves}</td>
        <td>{team.points}</td>
      </tr>
    ));

  return (
    <div>
      <table className="scoreboard">
        <thead>
          <tr><th>#</th><th>Team</th><th>Ordered</th><th>Points</th></tr>
        </thead>
        <tbody>
          {teamRows}
        </tbody>
      </table>
    </div>
  );
}
Scoreboard.propTypes = {
  pointsByTeam: PropTypes.objectOf(PropTypes.number).isRequired,
  teamScoreboardOrder: PropTypes.arrayOf(PropTypes.object).isRequired,
};
export default Scoreboard;
