#!/usr/bin/env perl

use strict;
use warnings;
use feature qw(say);

use List::Util qw(max);
use Data::Dumper;

sub get_options {
   my %options;

   local $/;
   open my $fh, '<', './src/ima/options.py' or die $!;

   $_ = <$fh>;
   {
      if ( m/\G
            .*?
            \s* parser\.add_option \s* \(
            \s* (?: '(?<o>-\w)' \s*, )? \s* (?: '(?<o> --\w+(?: (?>-\w+)+ )? )' \s*, )?
            \s* (?<args>
                  (?:
                     \s* \w+ \s* =
                     (?:
                        \s*
                        (?: '(?: \\' | (?>[^'\\]*)  )*' | \d+ | False | True | None )
                     )+ ,?
                  )*
                )
            \s* \) \s*
            /gsxo ) {

         my $option = join ' ', grep { defined } @{$-{o}};

         if ( my $args = $+{args} ) {

            if ( $args =~ m/ \s* metavar \s* = \s* '(?<v>.+?)' /x ) {
               $options{$option}{v} = $+{v};
            }

            my $description;
            if ( $args =~ m/ \s* help \s* = (?: \s* '(?<d> (?: \\' | (?>[^'\\]*) )* )' (?{ $description .= $+{d} }) )+ /x ) {
               $options{$option}{d} = ( $description =~ s/`/\\`/gr );
            }
         }
         redo;
      }

   }

   return %options;
}

sub output_doc_options {
   my %options = @_;

   printf "**Mandatory arguments to long options are mandatory for short options too.**\n\n";

   foreach my $option ( keys %options ) {
      printf "\n\n### %s", ($option =~ s/ /, /r);
      printf ' %s', $options{$option}{v} if defined $options{$option}{v};
      printf "\n\n%s\n", $options{$option}{d};
   }
}

sub output_synopsis {
   my %options  = @_;
   my $synopsis = join ' ', map '[' . ( $_ =~ s/ /|/r ) . ( ( $options{$_}{v} // '' ) =~ s/(.+)/ **$1**/r ) . ']', keys %options;

   printf "## SYNOPSIS\n\n";
   printf "**ima** %s **QUERY** [..QUERY]\n\n", $synopsis;
}

sub output_authors {
   open my $fh, '<', './AUTHORS.md' or die $!;

   printf "# AUTHORS\n\n";
   while ( <$fh> ) {
      printf "%s\n", $1 if m/^\* (.+)$/;
   }
   say "";
}

sub output_file {
   my $file = shift;

   open my $fh, '<', $file or die $!;
   print while <$fh>;
   say "";
}

output_file('./utils/heading.md');

my %options = get_options();

output_synopsis(%options);

output_file('./utils/body.md');

output_doc_options(%options);

output_file('./utils/examples.md');
output_authors();
output_file('./utils/issues.md');
output_file('./utils/license.md');
