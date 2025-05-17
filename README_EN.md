# apex_sparrow_dart_calc

<br>English / [简体中文](README.md)<br><br>

The apex_sparrow_dart_calc repository provides a comprehensive shooting angle calculator for Sparrow’s Tracker Dart in Apex Legends, integrating data fitting, trajectory plotting, and a piecewise linear gravity model in four modules.

It first employs PyTorch to fit a nonlinear mapping from firing angle θ to gravity g based on experimental data, producing predictions across the full angle range.

Then it derives segmented linear functions for g(θ) approximation and implements dual/unique solution classification logic in the final calculator.

Users can input horizontal distance d and aiming angle θ_aim to obtain precise high and low firing angles, along with visualized ballistic trajectories.

## File Structure

- `theta_g_predictor.py` loads raw measurement data, trains and validates the neural network, and outputs θ→g predictions;
- `trajectory_plotter.py` reads the prediction file and plots projectile trajectories extended to a specified landing height;
- `piecewise_linear_g.py` generates and displays the piecewise linear g(θ) functions based on selected breakpoints;
- `sparrow_dart_calculator.py` combines all modules into a CLI tool for computing target hit angles and visualizing trajectories.

## Quick Start

After cloning the repository, ensure that Python dependencies (`pandas`, `numpy`, `torch`, `matplotlib`) are installed.
Run `sparrow_dart_calculator.py` to plot trajectories and calculate firing angles.

## Special Thanks

This project builds on:

- [NYTN02/APEX_thetacalculation](https://github.com/NYTN02/APEX_thetacalculation)
  We used the empirically determined firing speed (100.37 m/s) from this repository
  Author's Bilibili username: "猫盒喵", UID: 379405259

## License

Copyright (C) 2025 [leejch](https://github.com/leejch)

This project is licensed under the terms of the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).
You are free to use, modify, and distribute this software under GPLv3 or compatible licenses, provided that original copyright and license notices are preserved.

This software is provided "as is", without warranty of any kind, express or implied.
