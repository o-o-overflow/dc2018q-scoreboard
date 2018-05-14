import React from 'react';
import { Link, Route } from 'react-router-dom';
import ChallengeMenu from './ChallengeMenu';
import GameMatrix from './GameMatrix';
import Rules from './Rules';
import Scoreboard from './Scoreboard';

function challengePoints(solvers) {
  if (!Number.isInteger(solvers) || solvers < 2) return 500;
  return parseInt(100 + (400 / (1 + (0.08 * solvers * Math.log(solvers)))), 10);
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      challenges: {},
      lastSolveTimeByTeam: {},
      pointsByTeam: {},
      teamScoreboardOrder: [],
      showChallengeId: '',
      solvesByTeam: {},
      openedByCategory: {},
      unopened: {},
    };
    this.categoryByChallenge = {};
    this.challengeTitlesById = {};
  }

  componentDidMount() {
    this.loadData();
  }

  loadData = () => {
    fetch('data.json', { method: 'GET' })
      .then(response => response.json().then(body => ({ body, status: response.status })))
      .then(({ body, status }) => {
        if (status === 200) {
          this.processData(body.message);
        }
      });
  }

  processData = (data) => {
    const lastSolveTimeByTeam = {};
    const solvesByChallenge = {};
    const solvesByTeam = {};
    data.solves.forEach(([id, team, time]) => {
      if (id in solvesByChallenge) {
        solvesByChallenge[id] += 1;
      } else {
        solvesByChallenge[id] = 1;
      }

      if (team in solvesByTeam) {
        if (id !== 'mom') {
          lastSolveTimeByTeam[team] = Math.max(lastSolveTimeByTeam[team], time);
        }
        solvesByTeam[team].push(id);
      } else {
        lastSolveTimeByTeam[team] = time;
        solvesByTeam[team] = [id];
      }
    });

    const pointsByChallenge = {};
    const challenges = {};
    data.open.forEach(([id, title, tags, category]) => {
      this.categoryByChallenge[id] = category;
      this.challengeTitlesById[id] = title;
      pointsByChallenge[id] = challengePoints(solvesByChallenge[id]);

      const object = {
        id,
        points: pointsByChallenge[id],
        solveCount: solvesByChallenge[id] || 0,
        solved: (solvesByTeam[this.state.team] || []).includes(id),
        tags,
        title,
      };
      if (category in challenges) {
        challenges[category].push(object);
      } else {
        challenges[category] = [object];
      }
    });

    const pointsByTeam = {};
    Object.keys(solvesByTeam).forEach((team) => {
      let points = 0;
      solvesByTeam[team].forEach((id) => {
        points += pointsByChallenge[id];
      });
      pointsByTeam[team] = points;
    });

    const teamScoreboardOrder = Object.keys(pointsByTeam).map(name => ({
      lastSolveTime: lastSolveTimeByTeam[name],
      name,
      points: pointsByTeam[name],
      solves: solvesByTeam[name],
    }));
    teamScoreboardOrder.sort((a, b) => {
      if (a.points === b.points) {
        return a.lastSolveTime - b.lastSolveTime;
      }
      return b.points - a.points;
    });


    this.setState({
      ...this.state,
      challenges,
      lastSolveTimeByTeam,
      pointsByTeam,
      teamScoreboardOrder,
      solvesByTeam,
      unopened: data.unopened_by_category,
    });
  }

  render() {
    return (
      <div>
        <nav>
          <div className="nav-title"><a href="https://www.oooverflow.io">Order-of-the-Overflow</a></div>
          <input type="checkbox" id="nav-toggle" />
          <label htmlFor="nav-toggle" className="label-toggle">☰</label>
          <div className="nav-items">
            <Link to="/">À La Carte</Link>
            <Link to="/rules">Rules</Link>
            <Link to="/scoreboard">Scoreboard</Link>
            <Link to="/solves">Solves</Link>
            <a href="https://twitter.com/oooverflow">Announcements</a>
          </div>
        </nav>
        <div>
          <div className="background">
            <div className="background-fade" />
            <div className="container">
              <Route exact path="/" render={() => <ChallengeMenu challenges={this.state.challenges} unopened={this.state.unopened} />} />
              <Route exact path="/rules" component={Rules} />
              <Route exact path="/scoreboard" render={() => <Scoreboard categoryByChallenge={this.categoryByChallenge} pointsByTeam={this.state.pointsByTeam} teamScoreboardOrder={this.state.teamScoreboardOrder} />} />
              <Route exact path="/solves" render={() => <GameMatrix challenges={this.state.challenges} teamScoreboardOrder={this.state.teamScoreboardOrder} />} />
            </div>
          </div>
        </div>
      </div>
    );
  }
}
export default App;
