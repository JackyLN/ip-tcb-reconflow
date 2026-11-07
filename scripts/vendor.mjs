import {copyFileSync} from 'node:fs';
copyFileSync('node_modules/htmx.org/dist/htmx.min.js', 'reconflow/static/htmx.min.js');
copyFileSync('node_modules/chart.js/dist/chart.umd.js', 'reconflow/static/chart.umd.js');
