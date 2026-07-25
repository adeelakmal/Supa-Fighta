const {
    RegExpMatcher,
    englishDataset,
    englishRecommendedTransformers
} = require('obscenity');

const matcher = new RegExpMatcher({
    ...englishDataset.build(),
    ...englishRecommendedTransformers
});

// These are harmful or impersonating terms that are not part of the
// profanity dataset. Keep this list compact and review additions manually.
const ADDITIONAL_BLOCKED_NAMES = new Set([
    '1488',
    'heilhitler',
    'hitler',
    'kkk',
    'nazi',
    'whitepower'
]);

const LEET_REPLACEMENTS = {
    '0': 'o',
    '1': 'i',
    '3': 'e',
    '4': 'a',
    '5': 's',
    '7': 't'
};

const compactPlayerName = (name) => (
    name
        .toLowerCase()
        .replace(/[ _-]+/g, '')
);

const foldCommonLeet = (name) => (
    name.replace(/[013457]/g, character => LEET_REPLACEMENTS[character])
);

const isAdditionalBlockedName = (name) => {
    const compact = compactPlayerName(name);
    const withoutTrailingNumbers = compact.replace(/\d+$/g, '');
    const forms = new Set([
        compact,
        withoutTrailingNumbers,
        foldCommonLeet(compact),
        foldCommonLeet(withoutTrailingNumbers)
    ]);

    return [...forms].some(form => ADDITIONAL_BLOCKED_NAMES.has(form));
};

const isPlayerNameOffensive = (name) => {
    const compact = compactPlayerName(name);
    return (
        matcher.hasMatch(name)
        || matcher.hasMatch(compact)
        || isAdditionalBlockedName(name)
    );
};

module.exports = {
    compactPlayerName,
    isPlayerNameOffensive
};
