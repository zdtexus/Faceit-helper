var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var _this = this;
document.addEventListener('DOMContentLoaded', function () {
    var regions = ['EU', 'NA', 'SA'];
    var limit = 100;
    var maxPlayers = 900;
    var offset = { 'EU': 100, 'NA': 100, 'SA': 100 };
    regions.forEach(function (region) {
        var rankingContainer = document.getElementById("".concat(region.toLowerCase(), "-ranking-container"));
        var loading = document.getElementById("".concat(region.toLowerCase(), "-loading"));
        var totalPlayersLoaded = 0;
        if (!rankingContainer || !loading) {
            console.error("Could not find elements for region ".concat(region));
            return;
        }
        var loadMoreRankings = function () { return __awaiter(_this, void 0, void 0, function () {
            var response, data, error_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (totalPlayersLoaded >= maxPlayers)
                            return [2];
                        loading.style.display = 'block';
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 4, 5, 6]);
                        return [4 , fetch("/load_more_rankings?region=".concat(region, "&offset=").concat(offset[region], "&limit=").concat(limit))];
                    case 2:
                        response = _a.sent();
                        return [4 , response.json()];
                    case 3:
                        data = _a.sent();
                        if (data.length > 0) {
                            data.forEach(function (player) {
                                if (totalPlayersLoaded >= maxPlayers)
                                    return;
                                var playerDiv = document.createElement('div');
                                playerDiv.classList.add('top20elo-item');
                                var rankHTML = player.rank === "9-1000" ? "\n                            <div class=\"top20elo-rank-9-1000\">\n                                <pre>#</pre>".concat(player.position, "\n                                <img title=\"Faceit Challenger 9-1000\" class=\"fc-9-1000\" src=\"../static/images/No.4-1000.svg\" alt=\"wood\" width=\"20\" height=\"20\">\n                            </div>") : '';
                                playerDiv.innerHTML = "\n                            <div class=\"top20elo-ranks\">".concat(rankHTML, "</div>\n                            <div class=\"top20elo-nickname\">\n                                <img class=\"top20elo-flag\" src=\"/static/flags/").concat(player.country.toLowerCase(), ".svg\" alt=\"").concat(player.country, "\" width=\"20\" height=\"15\">\n                                <a href=\"/").concat(player.nickname, "\">").concat(player.nickname, "</a>\n                            </div>\n                            <div class=\"top20elo-elo\">").concat(player.faceit_elo, "</div>\n                        ");
                                rankingContainer.appendChild(playerDiv);
                                totalPlayersLoaded++;
                            });
                            offset[region] += limit;
                        }
                        return [3 , 6];
                    case 4:
                        error_1 = _a.sent();
                        console.error('Error loading more rankings:', error_1);
                        return [3 , 6];
                    case 5:
                        if (loading) {
                            loading.style.display = 'none';
                        }
                        return [7];
                    case 6: return [2];
                }
            });
        }); };
        if (rankingContainer) {
            rankingContainer.addEventListener('scroll', function () {
                if (rankingContainer.scrollTop + rankingContainer.clientHeight >= rankingContainer.scrollHeight - 10) {
                    loadMoreRankings();
                }
            });
        }
    });
    var cs2Stats = document.querySelector('.cs2-stats');
    var lifetimeStats = document.querySelector('.main-stats');
    var toggleLeft = document.querySelector('.main-toggle-button-left');
    var toggleRight = document.querySelector('.main-toggle-button-right');
    var handleToggle = function (showCs2Stats) {
        if (cs2Stats && lifetimeStats && toggleLeft && toggleRight) {
            cs2Stats.style.display = showCs2Stats ? 'grid' : 'none';
            lifetimeStats.style.display = showCs2Stats ? 'none' : 'grid';
            toggleLeft.style.display = showCs2Stats ? 'none' : 'grid';
            toggleRight.style.display = showCs2Stats ? 'grid' : 'none';
        }
    };
    if (toggleLeft && toggleRight) {
        toggleLeft.addEventListener('click', function () { return handleToggle(true); });
        toggleRight.addEventListener('click', function () { return handleToggle(false); });
    }
    var statsItems = document.querySelectorAll('.stats-item');
    var currentIndex = 0;
    var updateVisibility = function () {
        statsItems.forEach(function (item, index) {
            item.style.display = (index === currentIndex) ? 'grid' : 'none';
        });
    };
    document.querySelectorAll('.last-50-toggle-button-left, .last-100-toggle-button-left').forEach(function (button) {
        button.addEventListener('click', function () {
            currentIndex = (currentIndex === 0) ? statsItems.length - 1 : currentIndex - 1;
            updateVisibility();
        });
    });
    document.querySelectorAll('.last-20-toggle-button-right, .last-50-toggle-button-right').forEach(function (button) {
        button.addEventListener('click', function () {
            currentIndex = (currentIndex === statsItems.length - 1) ? 0 : currentIndex + 1;
            updateVisibility();
        });
    });
    var matchToggle = document.getElementById('match-toggle');
    var mapsToggle = document.getElementById('maps-toggle');
    var matchesSection = document.getElementById('matches-section');
    var mapsSection = document.getElementById('maps-section');
    if (matchToggle && mapsToggle && matchesSection && mapsSection) {
        matchToggle.addEventListener('click', function () {
            matchesSection.style.display = 'block';
            mapsSection.style.display = 'none';
            matchToggle.classList.add('active');
            mapsToggle.classList.remove('active');
        });
        mapsToggle.addEventListener('click', function () {
            mapsSection.style.display = 'block';
            matchesSection.style.display = 'none';
            mapsToggle.classList.add('active');
            matchToggle.classList.remove('active');
        });
        matchToggle.click();
    }
});
