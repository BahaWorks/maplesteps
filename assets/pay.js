// MapleSteps take-home pay calculator — 2026 estimate.
// Sources: CRA T4127 (Jan 2026), CRA 2026 tax rates, Revenu Québec 2026 changes,
// BC Budget 2026 (lowest rate 5.6%, BC tax reduction $690), Manitoba Budget 2026 (indexation paused).
(function () {
  var INF = Infinity;
  var R = {
    fed: { br: [[58523, .14], [117045, .205], [181440, .26], [258482, .29], [INF, .33]],
           bpaMax: 16452, bpaMin: 14829, bpaLo: 181440, bpaHi: 258482, cea: 1501, low: .14, qcAbate: .165 },
    cpp: { ympe: 74600, yampe: 85000, ex: 3500, base: .0495, first: .01, second: .04 },
    qpp: { base: .053, first: .01, second: .04 },
    ei: { mie: 68900, rate: .0163, qc: .013 },
    qpip: { max: 103000, rate: .0043 },
    prov: {
      ON: { br: [[53891, .0505], [107785, .0915], [150000, .1116], [220000, .1216], [INF, .1316]], bpa: 12989 },
      QC: { br: [[54345, .14], [108680, .19], [132245, .24], [INF, .2575]], bpa: 18952, workerMax: 1450, workerRate: .06 },
      BC: { br: [[50363, .056], [100728, .077], [115648, .105], [140430, .1229], [190405, .147], [265545, .168], [INF, .205]], bpa: 13216,
            red: 690, redLo: 25570, redRate: .0356 },
      AB: { br: [[61200, .08], [154259, .10], [185111, .12], [246813, .13], [370220, .14], [INF, .15]], bpa: 22769, supp: 4896 },
      MB: { br: [[47000, .108], [100000, .1275], [INF, .174]], bpa: 15780, bpaLo: 200000, bpaHi: 400000 },
      NS: { br: [[30995, .0879], [61991, .1495], [97417, .1667], [157124, .175], [INF, .21]], bpa: 11932 }
    }
  };

  function bracket(inc, br) {
    var tax = 0, prev = 0;
    for (var i = 0; i < br.length; i++) {
      var top = br[i][0], rate = br[i][1];
      if (inc <= prev) break;
      tax += (Math.min(inc, top) - prev) * rate;
      prev = top;
    }
    return tax;
  }

  function compute(gross, prov) {
    var qc = prov === 'QC', P = R.prov[prov];
    var pens = Math.max(0, Math.min(gross, R.cpp.ympe) - R.cpp.ex);
    var baseRate = qc ? R.qpp.base : R.cpp.base;
    var pBase = pens * baseRate, pFirst = pens * R.cpp.first;
    var pSecond = Math.max(0, Math.min(gross, R.cpp.yampe) - R.cpp.ympe) * R.cpp.second;
    var pension = pBase + pFirst + pSecond;
    var ei = Math.min(gross, R.ei.mie) * (qc ? R.ei.qc : R.ei.rate);
    var qpip = qc ? Math.min(gross, R.qpip.max) * R.qpip.rate : 0;
    var taxable = Math.max(0, gross - pFirst - pSecond);

    // Federal
    var F = R.fed, bpa = F.bpaMax;
    if (taxable > F.bpaHi) bpa = F.bpaMin;
    else if (taxable > F.bpaLo) bpa = F.bpaMax - (taxable - F.bpaLo) * (F.bpaMax - F.bpaMin) / (F.bpaHi - F.bpaLo);
    var fedCredits = F.low * (bpa + Math.min(F.cea, gross) + pBase + ei + qpip);
    var fed = Math.max(0, bracket(taxable, F.br) - fedCredits);
    if (qc) fed *= (1 - F.qcAbate);

    // Provincial
    var pt = 0, low = P.br[0][1];
    if (qc) {
      var qTaxable = Math.max(0, taxable - Math.min(P.workerMax, gross * P.workerRate));
      pt = Math.max(0, bracket(qTaxable, P.br) - low * P.bpa);
    } else {
      var pbpa = P.bpa;
      if (P.bpaLo && taxable > P.bpaLo) pbpa = Math.max(0, P.bpa * (1 - (taxable - P.bpaLo) / (P.bpaHi - P.bpaLo)));
      var credits = low * (pbpa + pBase + ei);
      if (P.supp && credits > P.supp) credits += (credits - P.supp) * 0.25;
      pt = Math.max(0, bracket(taxable, P.br) - credits);
      if (prov === 'ON') {
        var sur = 0;
        if (pt > 5818) sur += .20 * (pt - 5818);
        if (pt > 7446) sur += .36 * (pt - 7446);
        pt += sur;
        pt = Math.max(0, pt - Math.max(0, 2 * 300 - pt));
        pt += onHealth(taxable);
      }
      if (prov === 'BC') {
        var red = taxable <= P.redLo ? P.red : Math.max(0, P.red - (taxable - P.redLo) * P.redRate);
        pt = Math.max(0, pt - red);
      }
    }
    var net = gross - fed - pt - pension - ei - qpip;
    return { gross: gross, fed: fed, prov: pt, cpp: qc ? 0 : pension, qpp: qc ? pension : 0, ei: ei, qpip: qpip, net: net };
  }

  function onHealth(t) {
    if (t <= 20000) return 0;
    if (t <= 36000) return Math.min(300, .06 * (t - 20000));
    if (t <= 48000) return Math.min(450, 300 + .06 * (t - 36000));
    if (t <= 72000) return Math.min(600, 450 + .25 * (t - 48000));
    if (t <= 200000) return Math.min(750, 600 + .25 * (t - 72000));
    return Math.min(900, 750 + .25 * (t - 200000));
  }

  window.MapleStepsPay = { compute: compute, rates: R };

  var root = document.querySelector('.calc');
  if (!root) return;
  var locale = root.getAttribute('data-locale') || 'en-CA';
  var T = JSON.parse(root.querySelector('.c-i18n').textContent);
  var f = root.querySelector('.c-form');
  var money;
  try { money = new Intl.NumberFormat(locale, { style: 'currency', currency: 'CAD', currencyDisplay: 'narrowSymbol', maximumFractionDigits: 0 }); }
  catch (e) { money = new Intl.NumberFormat(locale, { style: 'currency', currency: 'CAD', maximumFractionDigits: 0 }); }
  var pct = new Intl.NumberFormat(locale, { style: 'percent', maximumFractionDigits: 0 });
  var hoursBox = root.querySelector('.c-hours');
  var FACT = { year: 1, month: 12, biweek: 26, week: 52 };

  function num(v) {
    v = String(v || '').replace(/[\s,$]/g, '').replace(/[٠-٩]/g, function (d) { return d.charCodeAt(0) - 1632; })
      .replace(/[۰-۹]/g, function (d) { return d.charCodeAt(0) - 1776; }).replace('٫', '.');
    var n = parseFloat(v);
    return isFinite(n) && n > 0 ? n : 0;
  }

  function update() {
    var per = f.per.value;
    hoursBox.hidden = per !== 'hour';
    var amount = num(f.pay.value), hours = num(f.hours.value) || 40;
    var gross = per === 'hour' ? amount * hours * 52 : amount * (FACT[per] || 1);
    var prov = f.prov.value;
    root.querySelectorAll('tr[data-row]').forEach(function (tr) {
      var k = tr.getAttribute('data-row');
      tr.hidden = (prov === 'QC' && k === 'cpp') || (prov !== 'QC' && (k === 'qpp' || k === 'qpip'));
    });
    if (!gross) {
      root.querySelectorAll('[data-out],[data-y],[data-m]').forEach(function (el) { el.textContent = '–'; });
      root.querySelector('.c-avg').textContent = T.empty;
      return;
    }
    var r = compute(gross, prov);
    Object.keys(FACT).forEach(function (k) {
      root.querySelector('[data-out="' + k + '"]').textContent = money.format(r.net / FACT[k]);
    });
    Object.keys(r).forEach(function (k) {
      var y = root.querySelector('[data-y="' + k + '"]'), m = root.querySelector('[data-m="' + k + '"]');
      var sign = (k === 'gross' || k === 'net') ? '' : '−';
      if (y) y.textContent = sign + money.format(r[k]);
      if (m) m.textContent = sign + money.format(r[k] / 12);
    });
    root.querySelector('.c-avg').textContent = T.avg.replace('{pct}', pct.format((gross - r.net) / gross));
  }

  f.addEventListener('input', update);
  f.addEventListener('change', update);
  update();
})();
