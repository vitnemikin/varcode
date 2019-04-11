#!/usr/bin/perl
use 5.010;
use strict;
use warnings;  no warnings 'experimental::smartmatch';
use Time::HiRes ('sleep');
use IO::Prompter;


my ($fileName) = @ARGV;
die "Не указан файл игры.\n" unless $fileName;

our %game = ();
require $fileName;
die "Что-то не то с файлом игры.\n" unless ($game{NAME} && $game{SCENE_0});



my $game_end = 0;
my $currentScene = 'SCENE_0';
my @pocketItems  = ();
my @passedScenes = ();
my @availActions = ();

say "Добро пожаловать в игру $game{NAME}!";
say "Автор игры: $game{AUTHOR}";
say "Нажмите любую клавишу, чтобы начать.";
my $c = <STDIN>;

Pause();
GameScene();
until ($game_end) {
	GameAction();
}

printf "Конец.\n\n";




sub GameScene {
	Disappear();
	ShowDescription();
	printf "\n";
	ShowPocket();
	printf "\n";
	ShowActions();
}


sub GameAction {
	if (!$game{$currentScene}{ACTIONS}) {
		$game_end = 1;
		return;
	}

	my $act = GetAction();
	return if ($act < 0);
	my $effect = $act->{EFFECT};

	if ($effect->{COLLECT}) {
		push @pocketItems, $effect->{COLLECT};
	}
	if ($effect->{DISPOSE}) {
		@pocketItems = grep {$_ ne $effect->{DISPOSE}} @pocketItems;
	}
	if ($effect->{ALERT}) {
			Disappear();
			say $effect->{ALERT};
			my $c = <STDIN>;
			GameScene();
	}

	if ($effect->{GO}) {
		if ($currentScene ne $effect->{GO}) {
			push @passedScenes, $currentScene;
			$currentScene = $effect->{GO};
			GameScene();
		}
	}	

}


sub GetAction {
	#printf "> ";
	#my $c = <STDIN>;
	#chomp $c;
    my @autocomplist = ();
	for my $action (@availActions) {
		push @autocomplist, $action->{NAME};
	}
	
    my $c = prompt -complete => \@autocomplist;
	Pause();
	printf "> ";

	for my $action (@availActions) {
		if ($c eq $action->{NAME}) { return $action; }
	}
	return -1;
}


sub ShowDescription {
	my $text = $game{$currentScene}{DESCRIPTION};
	$text =~ s/\n/|/g;
	$text =~ s/\s+/ /g;
	$text =~ s/\|/\n /g;
	say "$text";
}


sub ShowPocket {
	return unless $game{$currentScene}{ACTIONS};

	my $text = "У тебя есть:  ";
	if ($#pocketItems < 0) {
		$text .= "ничего, ";
	}
	else {
		for my $i (@pocketItems) {
			$text .= $i . ", ";
		}
	}
	say substr ($text, 0, -2);
}


sub ShowActions {
	return unless $game{$currentScene}{ACTIONS};

	my $text = "Что будешь делать? (";
	my $whenOk;
	my $act_array = $game{$currentScene}{ACTIONS};
	@availActions = ();
	
	for my $action (@$act_array) {
		$whenOk = 1;
		if ($action->{WHEN}) {

			if ($action->{WHEN}{HAVE})
				{ $whenOk &= ($action->{WHEN}{HAVE} ~~ @pocketItems); }

			if ($action->{WHEN}{LACK})
				{ $whenOk &= !($action->{WHEN}{LACK} ~~ @pocketItems); }

			if ($action->{WHEN}{PASSED})
				{ $whenOk &= ($currentScene ~~ @passedScenes); }

			if ($action->{WHEN}{MISSED}) 
				{ $whenOk &= !($currentScene ~~ @passedScenes); }
		}

		if ($whenOk) { 
			$text .= $action->{NAME} . ", ";
			push @availActions, $action;
		}

	}
	say substr ($text, 0, -2) . ")\n";
}


sub Pause {
	for my $i (0..5) {
		sleep(0.1);
		printf ".";
	}	
}


sub Disappear {
	printf "\e[2J";
}
