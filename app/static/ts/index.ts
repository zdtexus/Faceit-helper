document.addEventListener('DOMContentLoaded', () => {
    // Code from index.ts
    const regions: string[] = ['EU', 'NA', 'SA'];
    const limit: number = 100;
    const maxPlayers: number = 900;
    let offset: { [key: string]: number } = { 'EU': 100, 'NA': 100, 'SA': 100 };

    regions.forEach(region => {
        const rankingContainer = document.getElementById(`${region.toLowerCase()}-ranking-container`) as HTMLElement | null;
        const loading = document.getElementById(`${region.toLowerCase()}-loading`) as HTMLElement | null;
        let totalPlayersLoaded = 0;

        if (!rankingContainer || !loading) {
            console.error(`Could not find elements for region ${region}`);
            return; // Exit current iteration if elements are not found
        }

        const loadMoreRankings = async () => {
            if (totalPlayersLoaded >= maxPlayers) return;

            loading.style.display = 'block';

            try {
                const response = await fetch(`/load_more_rankings?region=${region}&offset=${offset[region]}&limit=${limit}`);
                const data = await response.json();

                if (data.length > 0) {
                    data.forEach((player: any) => {
                        if (totalPlayersLoaded >= maxPlayers) return;

                        const playerDiv = document.createElement('div');
                        playerDiv.classList.add('top20elo-item');

                        const rankHTML = player.rank === "9-1000" ? `
                            <div class="top20elo-rank-9-1000">
                                <pre>#</pre>${player.position}
                                <img title="Faceit Challenger 9-1000" class="fc-9-1000" src="../static/images/No.4-1000.svg" alt="wood" width="20" height="20">
                            </div>` : '';

                        playerDiv.innerHTML = `
                            <div class="top20elo-ranks">${rankHTML}</div>
                            <div class="top20elo-nickname">
                                <img class="top20elo-flag" src="/static/flags/${player.country.toLowerCase()}.svg" alt="${player.country}" width="20" height="15">
                                <a href="/${player.nickname}">${player.nickname}</a>
                            </div>
                            <div class="top20elo-elo">${player.faceit_elo}</div>
                        `;

                        rankingContainer.appendChild(playerDiv);
                        totalPlayersLoaded++;
                    });

                    offset[region] += limit;
                }
            } catch (error) {
                console.error('Error loading more rankings:', error);
            } finally {
                if (loading) {
                    loading.style.display = 'none';
                }
            }
        };

        if (rankingContainer) {
            rankingContainer.addEventListener('scroll', () => {
                if (rankingContainer.scrollTop + rankingContainer.clientHeight >= rankingContainer.scrollHeight - 10) {
                    loadMoreRankings();
                }
            });
        }
    });

    const cs2Stats = document.querySelector('.cs2-stats') as HTMLElement | null;
    const lifetimeStats = document.querySelector('.main-stats') as HTMLElement | null;
    const toggleLeft = document.querySelector('.main-toggle-button-left') as HTMLElement | null;
    const toggleRight = document.querySelector('.main-toggle-button-right') as HTMLElement | null;

    const handleToggle = (showCs2Stats: boolean) => {
        if (cs2Stats && lifetimeStats && toggleLeft && toggleRight) {
            cs2Stats.style.display = showCs2Stats ? 'grid' : 'none';
            lifetimeStats.style.display = showCs2Stats ? 'none' : 'grid';
            toggleLeft.style.display = showCs2Stats ? 'none' : 'grid';
            toggleRight.style.display = showCs2Stats ? 'grid' : 'none';
        }
    };

    if (toggleLeft && toggleRight) {
        toggleLeft.addEventListener('click', () => handleToggle(true));
        toggleRight.addEventListener('click', () => handleToggle(false));
    }

    const statsItems = document.querySelectorAll('.stats-item') as NodeListOf<HTMLElement>;
    let currentIndex = 0;

    const updateVisibility = () => {
        statsItems.forEach((item, index) => {
            item.style.display = (index === currentIndex) ? 'grid' : 'none';
        });
    };

    document.querySelectorAll('.last-50-toggle-button-left, .last-100-toggle-button-left').forEach(button => {
        button.addEventListener('click', () => {
            currentIndex = (currentIndex === 0) ? statsItems.length - 1 : currentIndex - 1;
            updateVisibility();
        });
    });

    document.querySelectorAll('.last-20-toggle-button-right, .last-50-toggle-button-right').forEach(button => {
        button.addEventListener('click', () => {
            currentIndex = (currentIndex === statsItems.length - 1) ? 0 : currentIndex + 1;
            updateVisibility();
        });
    });

    const matchToggle = document.getElementById('match-toggle');
    const mapsToggle = document.getElementById('maps-toggle');
    const matchesSection = document.getElementById('matches-section');
    const mapsSection = document.getElementById('maps-section');

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
